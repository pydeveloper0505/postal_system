from django.db import models
from django.conf import settings
from orders.models import Order


class CourierAssignment(models.Model):
    courier     = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='assignments',
        limit_choices_to={'role': 'courier'},
    )
    order       = models.OneToOneField(
        Order,
        on_delete=models.CASCADE,
        related_name='courier_assignment',
    )
    assigned_at = models.DateTimeField(auto_now_add=True)
    notes       = models.TextField(blank=True)

    class Meta:
        ordering = ['-assigned_at']

    def __str__(self):
        return f'{self.courier.username} → {self.order.tracking_code}'
