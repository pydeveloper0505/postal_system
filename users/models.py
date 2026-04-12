from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ROLE_SENDER  = 'sender'
    ROLE_COURIER = 'courier'
    ROLE_ADMIN   = 'admin'

    ROLE_CHOICES = [
        (ROLE_SENDER,  'Sender'),
        (ROLE_COURIER, 'Courier'),
        (ROLE_ADMIN,   'Admin'),
    ]

    role  = models.CharField(max_length=20, choices=ROLE_CHOICES, default=ROLE_SENDER)
    phone = models.CharField(max_length=20, blank=True)
    bio   = models.TextField(blank=True)

    def is_sender(self):  return self.role == self.ROLE_SENDER
    def is_courier(self): return self.role == self.ROLE_COURIER
    def is_admin(self):   return self.role == self.ROLE_ADMIN or self.is_staff

    def __str__(self):
        return f'{self.get_full_name() or self.username} ({self.role})'


class Address(models.Model):
    user     = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses')
    title    = models.CharField(max_length=100, help_text='e.g. Home, Office')
    region   = models.CharField(max_length=100)
    city     = models.CharField(max_length=100)
    street   = models.CharField(max_length=200)
    house    = models.CharField(max_length=20)
    zip_code = models.CharField(max_length=10, blank=True)
    is_default = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = 'Addresses'

    def full_address(self):
        return f'{self.region}, {self.city}, {self.street} {self.house}'

    def __str__(self):
        return f'{self.title} – {self.full_address()}'
