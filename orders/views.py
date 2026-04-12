from django.views.generic import TemplateView, ListView, DetailView, CreateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, get_object_or_404, render
from django.urls import reverse_lazy
from django.contrib import messages
from .models import Order
from .forms import OrderForm
from notifications.utils import create_notification


class HomeView(TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['features'] = [
            ('house-door',   'Pickup From Home',   'No need to visit a branch. We come to you.'),
            ('shield-check', 'Safe & Insured',      'Your parcels are protected end-to-end.'),
            ('geo-alt-fill', 'Real-time Tracking',  'Track your parcel at every step.'),
        ]
        return ctx


class OrderListView(LoginRequiredMixin, ListView):
    model               = Order
    template_name       = 'orders/order_list.html'
    context_object_name = 'orders'
    paginate_by         = 10

    def get_queryset(self):
        user = self.request.user
        if user.is_courier():
            return Order.objects.filter(
                courier_assignment__courier=user
            ).select_related('sender', 'pickup_address')
        return Order.objects.filter(
            sender=user
        ).select_related('pickup_address', 'delivery_address')


class OrderDetailView(LoginRequiredMixin, DetailView):
    model               = Order
    template_name       = 'orders/order_detail.html'
    context_object_name = 'order'

    def get_queryset(self):
        user = self.request.user
        if user.is_courier():
            return Order.objects.filter(courier_assignment__courier=user)
        if user.is_staff:
            return Order.objects.all()
        return Order.objects.filter(sender=user)


class OrderCreateView(LoginRequiredMixin, CreateView):
    model         = Order
    form_class    = OrderForm
    template_name = 'orders/order_form.html'
    success_url   = reverse_lazy('orders:list')

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and not request.user.is_sender():
            messages.error(request, 'Only senders can create orders.')
            return redirect('orders:list')
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.sender = self.request.user
        response = super().form_valid(form)
        create_notification(
            user    = self.request.user,
            title   = 'Order created',
            message = f'Your order #{self.object.tracking_code} has been placed. '
                      f'Price: {self.object.price} UZS'
        )
        messages.success(self.request, f'Order {self.object.tracking_code} created!')
        return response


class MockPaymentView(LoginRequiredMixin, View):
    """Simulate payment — no real gateway needed."""

    def get(self, request, pk):
        order = get_object_or_404(Order, pk=pk, sender=request.user)
        return render(request, 'orders/payment.html', {'order': order})

    def post(self, request, pk):
        order = get_object_or_404(Order, pk=pk, sender=request.user)
        order.is_paid = True
        order.save()
        create_notification(
            user    = request.user,
            title   = 'Payment confirmed',
            message = f'Payment for order #{order.tracking_code} confirmed.'
        )
        messages.success(request, 'Payment successful!')
        return redirect('orders:detail', pk=order.pk)


class TrackOrderView(TemplateView):
    template_name = 'orders/track.html'

    def get_context_data(self, **kwargs):
        ctx  = super().get_context_data(**kwargs)
        code = self.request.GET.get('code', '').strip()
        ctx['code'] = code
        if code:
            try:
                ctx['order'] = Order.objects.get(tracking_code=code)
            except Order.DoesNotExist:
                ctx['not_found'] = True
        return ctx
