from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import redirect


class CourierRequiredMixin(UserPassesTestMixin):
    """Allow only users with courier role."""
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_courier()

    def handle_no_permission(self):
        return redirect('orders:list')
