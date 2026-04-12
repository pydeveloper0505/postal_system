from django.views.generic import CreateView, UpdateView, ListView, CreateView, DetailView
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import login
from django.urls import reverse_lazy
from django.shortcuts import redirect, get_object_or_404
from django.db.models import Avg, Count

from .models import User, Address, CourierProfile, CourierReview
from .forms import RegisterForm, LoginForm, ProfileForm, AddressForm, CourierReviewForm
from .mixins import SenderRequiredMixin, AdminRequiredMixin


class RegisterView(CreateView):
    model         = User
    form_class    = RegisterForm
    template_name = 'users/register.html'
    success_url   = reverse_lazy('orders:list')

    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)
        return response

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('orders:list')
        return super().dispatch(request, *args, **kwargs)


class CustomLoginView(LoginView):
    form_class    = LoginForm
    template_name = 'users/login.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('orders:list')
        return super().dispatch(request, *args, **kwargs)


class CustomLogoutView(LogoutView):
    next_page = '/'


class ProfileView(LoginRequiredMixin, UpdateView):
    model         = User
    form_class    = ProfileForm
    template_name = 'users/profile.html'
    success_url   = reverse_lazy('users:profile')

    def get_object(self):
        return self.request.user

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        user = self.request.user
        if user.is_courier:
            ctx['courier_profile'] = getattr(user, 'courier_profile', None)
        return ctx


class AddressListView(LoginRequiredMixin, ListView):
    model               = Address
    template_name       = 'users/address_list.html'
    context_object_name = 'addresses'

    def get_queryset(self):
        return Address.objects.filter(user=self.request.user)


class AddressCreateView(LoginRequiredMixin, CreateView):
    model         = Address
    form_class    = AddressForm
    template_name = 'users/address_form.html'
    success_url   = reverse_lazy('users:addresses')

    def form_valid(self, form):
        form.instance.user = self.request.user
        if form.cleaned_data.get('is_default'):
            Address.objects.filter(user=self.request.user).update(is_default=False)
        return super().form_valid(form)


# ── Admin: Courier list ────────────────────────────────────────────────────────
class CourierListView(AdminRequiredMixin, ListView):
    """Admin sees all couriers with their status and rating."""
    template_name       = 'users/courier_list.html'
    context_object_name = 'couriers'

    def get_queryset(self):
        return User.objects.filter(role=User.Role.COURIER).select_related(
            'courier_profile'
        ).prefetch_related('assignments')


class CourierDetailView(LoginRequiredMixin, DetailView):
    """Public courier profile — visible to all authenticated users."""
    model               = User
    template_name       = 'users/courier_detail.html'
    context_object_name = 'courier'

    def get_queryset(self):
        return User.objects.filter(role=User.Role.COURIER).select_related('courier_profile')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['reviews'] = self.object.received_reviews.select_related('sender', 'order')[:10]
        return ctx


# ── Sender: Leave review after delivery ───────────────────────────────────────
class LeaveReviewView(SenderRequiredMixin, CreateView):
    model         = CourierReview
    form_class    = CourierReviewForm
    template_name = 'users/leave_review.html'

    def get_success_url(self):
        return reverse_lazy('orders:detail', kwargs={'pk': self.kwargs['order_pk']})

    def get_context_data(self, **kwargs):
        from orders.models import Order
        ctx = super().get_context_data(**kwargs)
        ctx['order'] = get_object_or_404(
            Order, pk=self.kwargs['order_pk'], sender=self.request.user
        )
        return ctx

    def form_valid(self, form):
        from orders.models import Order
        order = get_object_or_404(
            Order, pk=self.kwargs['order_pk'], sender=self.request.user
        )
        if not order.can_be_reviewed:
            from django.contrib import messages
            messages.error(self.request, 'Bu buyurtma uchun baho berish mumkin emas.')
            return redirect('orders:detail', pk=order.pk)
        form.instance.order   = order
        form.instance.sender  = self.request.user
        form.instance.courier = order.courier_assignment.courier
        return super().form_valid(form)
