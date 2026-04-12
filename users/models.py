import uuid
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class User(AbstractUser):
    """
    Custom user model with role-based access.
    Roles: sender, courier, admin (staff/superuser).
    """

    class Role(models.TextChoices):
        SENDER  = 'sender',  'Sender'
        COURIER = 'courier', 'Courier'
        ADMIN   = 'admin',   'Admin'

    role  = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.SENDER,
        db_index=True,
    )
    phone = models.CharField(max_length=20, blank=True)
    bio   = models.TextField(blank=True)

    # --- Role helpers ---
    @property
    def is_sender(self):
        return self.role == self.Role.SENDER

    @property
    def is_courier(self):
        return self.role == self.Role.COURIER

    @property
    def is_admin_user(self):
        return self.role == self.Role.ADMIN or self.is_staff or self.is_superuser

    def __str__(self):
        return f'{self.get_full_name() or self.username} ({self.role})'


class Address(models.Model):
    user       = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses')
    title      = models.CharField(max_length=100, help_text='e.g. Home, Office')
    region     = models.CharField(max_length=100)
    city       = models.CharField(max_length=100)
    street     = models.CharField(max_length=200)
    house      = models.CharField(max_length=20)
    zip_code   = models.CharField(max_length=10, blank=True)
    is_default = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = 'Addresses'

    def full_address(self):
        return f'{self.region}, {self.city}, {self.street} {self.house}'

    def __str__(self):
        return f'{self.title} – {self.full_address()}'


class CourierProfile(models.Model):
    """
    Extended profile for couriers:
    - availability status (FREE / BUSY) — updated via Signals
    - trust/rating score — updated on order review
    """

    class Status(models.TextChoices):
        FREE = 'free', 'Free'
        BUSY = 'busy', 'Busy'

    courier = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='courier_profile',
        limit_choices_to={'role': User.Role.COURIER},
    )
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.FREE,
        db_index=True,
    )
    # Rating: 0.0 – 5.0, auto-computed from reviews
    rating = models.FloatField(
        default=5.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(5.0)],
    )
    total_reviews      = models.PositiveIntegerField(default=0)
    vehicle_number     = models.CharField(max_length=20, blank=True)
    is_available       = models.BooleanField(default=True,
                                             help_text='Admin can deactivate courier manually')

    # Counters — updated via Signals (no extra DB queries on each request)
    active_orders_count    = models.PositiveIntegerField(default=0)
    delivered_count        = models.PositiveIntegerField(default=0)
    total_assigned_count   = models.PositiveIntegerField(default=0)

    def update_status(self):
        """FREE if no active orders, BUSY otherwise. Called from Signal."""
        if self.active_orders_count > 0:
            self.status = self.Status.BUSY
        else:
            self.status = self.Status.FREE
        self.save(update_fields=['status'])

    def recalculate_rating(self):
        """Weighted average from CourierReview. Called from Signal."""
        reviews = self.courier.received_reviews.aggregate(
            total=models.Count('id'),
            avg=models.Avg('score'),
        )
        self.total_reviews = reviews['total'] or 0
        self.rating = round(reviews['avg'] or 5.0, 2)
        self.save(update_fields=['rating', 'total_reviews'])

    def __str__(self):
        return f'{self.courier.username} – {self.status} – ⭐{self.rating}'


class CourierReview(models.Model):
    """Sender can leave a review for courier after delivery."""
    order   = models.OneToOneField(
        'orders.Order',
        on_delete=models.CASCADE,
        related_name='review',
    )
    courier = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='received_reviews',
        limit_choices_to={'role': User.Role.COURIER},
    )
    sender  = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='given_reviews',
    )
    score   = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
    )
    comment    = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Review for {self.courier.username}: {self.score}⭐'
