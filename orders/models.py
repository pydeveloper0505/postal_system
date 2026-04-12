import uuid
from django.db import models
from django.conf import settings
from users.models import Address


def generate_tracking_code():
    return 'UZ' + uuid.uuid4().hex[:8].upper()


class Order(models.Model):

    class Status(models.TextChoices):
        PENDING          = 'pending',          'Pending'
        PICKED_UP        = 'picked_up',        'Picked Up'
        IN_TRANSIT       = 'in_transit',       'In Transit'
        ARRIVED_BRANCH   = 'arrived_branch',   'Arrived at Branch'
        OUT_FOR_DELIVERY = 'out_for_delivery', 'Out for Delivery'
        DELIVERED        = 'delivered',        'Delivered'
        CANCELLED        = 'cancelled',        'Cancelled'

    class DeliveryType(models.TextChoices):
        BRANCH = 'branch', 'Branch Pickup'
        HOME   = 'home',   'Home Delivery'

    # Status progress order (for progress bar rendering)
    STATUS_PROGRESS = [
        Status.PENDING,
        Status.PICKED_UP,
        Status.IN_TRANSIT,
        Status.ARRIVED_BRANCH,
        Status.OUT_FOR_DELIVERY,
        Status.DELIVERED,
    ]

    # Sender
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sent_orders',
    )

    # Receiver info
    receiver_name  = models.CharField(max_length=150)
    receiver_phone = models.CharField(max_length=20)
    receiver_email = models.EmailField(blank=True)

    # Addresses
    pickup_address = models.ForeignKey(
        Address, on_delete=models.SET_NULL,
        null=True, related_name='pickup_orders',
    )
    delivery_address = models.ForeignKey(
        Address, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='delivery_orders',
    )

    # Parcel details
    weight        = models.FloatField(help_text='Weight in kg')
    description   = models.TextField()
    delivery_type = models.CharField(
        max_length=20,
        choices=DeliveryType.choices,
        default=DeliveryType.HOME,
    )

    # Insurance (Spetsifikatsiya 4: Safe & Insured)
    is_insured = models.BooleanField(default=False)

    # Status & payment
    status        = models.CharField(
        max_length=30,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True,
    )
    price         = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_paid       = models.BooleanField(default=False)
    tracking_code = models.CharField(max_length=20, unique=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.tracking_code:
            self.tracking_code = generate_tracking_code()
        if not self.price:
            self.price = self.calculate_price()
        super().save(*args, **kwargs)

    def calculate_price(self):
        BASE     = 10_000  # UZS
        PER_KG   = 5_000
        HOME_FEE = 15_000
        INSURANCE_FEE = 5_000
        price = BASE + (self.weight * PER_KG)
        if self.delivery_type == self.DeliveryType.HOME:
            price += HOME_FEE
        if self.is_insured:
            price += INSURANCE_FEE
        return round(price, 2)

    def get_status_badge(self):
        mapping = {
            self.Status.PENDING:          'warning',
            self.Status.PICKED_UP:        'info',
            self.Status.IN_TRANSIT:       'primary',
            self.Status.ARRIVED_BRANCH:   'secondary',
            self.Status.OUT_FOR_DELIVERY: 'info',
            self.Status.DELIVERED:        'success',
            self.Status.CANCELLED:        'danger',
        }
        return mapping.get(self.status, 'secondary')

    @property
    def progress_percent(self):
        """0–100 for progress bar. Cancelled = 0."""
        try:
            idx = self.STATUS_PROGRESS.index(self.status)
            return int((idx / (len(self.STATUS_PROGRESS) - 1)) * 100)
        except ValueError:
            return 0

    @property
    def is_active(self):
        return self.status not in (self.Status.DELIVERED, self.Status.CANCELLED)

    @property
    def can_be_reviewed(self):
        return self.status == self.Status.DELIVERED

    def __str__(self):
        return f'Order #{self.tracking_code} – {self.sender.username}'
