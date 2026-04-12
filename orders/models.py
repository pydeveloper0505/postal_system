import uuid
from django.db import models
from django.conf import settings
from users.models import Address


def generate_tracking_code():
    return 'UZ' + uuid.uuid4().hex[:8].upper()


class Order(models.Model):
    STATUS_PENDING          = 'pending'
    STATUS_PICKED_UP        = 'picked_up'
    STATUS_IN_TRANSIT       = 'in_transit'
    STATUS_ARRIVED_BRANCH   = 'arrived_branch'
    STATUS_OUT_FOR_DELIVERY = 'out_for_delivery'
    STATUS_DELIVERED        = 'delivered'
    STATUS_CANCELLED        = 'cancelled'

    STATUS_CHOICES = [
        (STATUS_PENDING,          'Pending'),
        (STATUS_PICKED_UP,        'Picked Up'),
        (STATUS_IN_TRANSIT,       'In Transit'),
        (STATUS_ARRIVED_BRANCH,   'Arrived at Branch'),
        (STATUS_OUT_FOR_DELIVERY, 'Out for Delivery'),
        (STATUS_DELIVERED,        'Delivered'),
        (STATUS_CANCELLED,        'Cancelled'),
    ]

    DELIVERY_BRANCH = 'branch'
    DELIVERY_HOME   = 'home'
    DELIVERY_CHOICES = [
        (DELIVERY_BRANCH, 'Branch Pickup'),
        (DELIVERY_HOME,   'Home Delivery'),
    ]

    # Relationships
    sender   = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                 related_name='sent_orders')
    receiver_name  = models.CharField(max_length=150)
    receiver_phone = models.CharField(max_length=20)
    receiver_email = models.EmailField(blank=True)

    pickup_address   = models.ForeignKey(Address, on_delete=models.SET_NULL,
                                         null=True, related_name='pickup_orders')
    delivery_address = models.ForeignKey(Address, on_delete=models.SET_NULL,
                                         null=True, blank=True, related_name='delivery_orders')

    # Parcel info
    weight      = models.FloatField(help_text='Weight in kg')
    description = models.TextField()
    delivery_type = models.CharField(max_length=20, choices=DELIVERY_CHOICES,
                                     default=DELIVERY_HOME)

    # Status & payment
    status        = models.CharField(max_length=30, choices=STATUS_CHOICES,
                                     default=STATUS_PENDING)
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
        """Simple price calculation: base + per-kg + delivery type fee."""
        BASE    = 10000   # UZS
        PER_KG  = 5000
        HOME_FEE = 15000
        price = BASE + (self.weight * PER_KG)
        if self.delivery_type == self.DELIVERY_HOME:
            price += HOME_FEE
        return round(price, 2)

    def get_status_badge(self):
        """Returns Bootstrap badge color for status."""
        mapping = {
            self.STATUS_PENDING:          'warning',
            self.STATUS_PICKED_UP:        'info',
            self.STATUS_IN_TRANSIT:       'primary',
            self.STATUS_ARRIVED_BRANCH:   'secondary',
            self.STATUS_OUT_FOR_DELIVERY: 'info',
            self.STATUS_DELIVERED:        'success',
            self.STATUS_CANCELLED:        'danger',
        }
        return mapping.get(self.status, 'secondary')

    def __str__(self):
        return f'Order #{self.tracking_code} – {self.sender.username}'
