"""
Custom permission mixins — UserPassesTestMixin subclasses.
Use these in all views to avoid repeating permission logic.
"""
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import redirect
from django.contrib import messages


class SenderRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Only active senders can access this view."""

    def test_func(self):
        return self.request.user.is_sender and self.request.user.is_active

    def handle_no_permission(self):
        messages.error(self.request, 'Bu sahifaga faqat jo\'natuvchilar kira oladi.')
        return redirect('orders:list')


class CourierRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Only couriers can access this view."""

    def test_func(self):
        return self.request.user.is_courier

    def handle_no_permission(self):
        messages.error(self.request, 'Bu sahifaga faqat kuryerlar kira oladi.')
        return redirect('orders:list')


class AdminRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Only staff/superuser/admin-role users."""

    def test_func(self):
        return self.request.user.is_admin_user

    def handle_no_permission(self):
        messages.error(self.request, 'Bu sahifaga faqat adminlar kira oladi.')
        return redirect('orders:list')
