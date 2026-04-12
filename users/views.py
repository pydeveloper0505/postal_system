from django.views.generic import CreateView, UpdateView, ListView, View
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import login
from django.urls import reverse_lazy
from django.shortcuts import redirect
from .models import User, Address
from .forms import RegisterForm, LoginForm, ProfileForm, AddressForm


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


class AddressListView(LoginRequiredMixin, ListView):
    model         = Address
    template_name = 'users/address_list.html'
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
        # If set as default, unset others
        if form.cleaned_data.get('is_default'):
            Address.objects.filter(user=self.request.user).update(is_default=False)
        return super().form_valid(form)
