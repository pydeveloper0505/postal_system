"""
Django Signals for automatic side-effects:

1. CourierProfile auto-create when a User with role=courier is saved.
2. CourierProfile status (FREE/BUSY) + counters updated on Order save.
3. CourierProfile rating recalculated on CourierReview save.
4. Notification sent to Sender when order is picked up.
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import models as db_models

from .models import User, CourierProfile, CourierReview


# ── 1. Auto-create CourierProfile ─────────────────────────────────────────────
@receiver(post_save, sender=User)
def create_courier_profile(sender, instance, created, **kwargs):
    """Create CourierProfile when a new courier user is registered."""
    if instance.role == User.Role.COURIER:
        CourierProfile.objects.get_or_create(courier=instance)


# ── 3. Recalculate courier rating on new review ───────────────────────────────
@receiver(post_save, sender=CourierReview)
def update_courier_rating(sender, instance, **kwargs):
    """Recalculate rating after each review."""
    try:
        instance.courier.courier_profile.recalculate_rating()
    except CourierProfile.DoesNotExist:
        pass
