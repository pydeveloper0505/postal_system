from django.views.generic import TemplateView, ListView, DetailView, CreateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, get_object_or_404, render
from django.urls import reverse_lazy
from django.contrib import messages
from django.db.models import Count, Q

from .models import Order
from .forms import OrderForm
from users.mixins import SenderRequiredMixin, CourierRequiredMixin, AdminRequiredMixin
from users.models import User, CourierProfile
from couriers.models import CourierAssignment
from notifications.utils import create_notification


# ── Public ────────────────────────────────────────────────────────────────────
class HomeView(TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['features'] = [
            ('house-door',   'Pickup From Home',
             'Kuryerimiz manzilингizга kelib yukingizни olib ketadi.'),
            ('shield-check', 'Safe & Insured',
             'Yuklarga sug\'urta xizmati mavjud. Xavfsiz yetkazamiz.'),
            ('geo-alt-fill', 'Real-time Tracking',
             'Yukingiz holatini har daqiqa kuzating.'),
        ]
        return ctx


class TrackOrderView(TemplateView):
    template_name = 'orders/track.html'

    def get_context_data(self, **kwargs):
        ctx  = super().get_context_data(**kwargs)
        code = self.request.GET.get('code', '').strip().upper()
        ctx['code'] = code
        if code:
            try:
                ctx['order'] = Order.objects.select_related(
                    'sender', 'pickup_address', 'delivery_address',
                    'courier_assignment__courier'
                ).get(tracking_code=code)
            except Order.DoesNotExist:
                ctx['not_found'] = True
        return ctx


# ── Sender ────────────────────────────────────────────────────────────────────
class OrderListView(LoginRequiredMixin, ListView):
    model               = Order
    template_name       = 'orders/order_list.html'
    context_object_name = 'orders'
    paginate_by         = 10

    def get_queryset(self):
        user = self.request.user
        if user.is_courier:
            return Order.objects.filter(
                courier_assignment__courier=user
            ).select_related('sender', 'pickup_address')
        if user.is_admin_user:
            return Order.objects.all().select_related(
                'sender', 'pickup_address', 'courier_assignment__courier'
            )
        # sender
        return Order.objects.filter(sender=user).select_related(
            'pickup_address', 'delivery_address'
        )


class OrderDetailView(LoginRequiredMixin, DetailView):
    model               = Order
    template_name       = 'orders/order_detail.html'
    context_object_name = 'order'

    def get_queryset(self):
        user = self.request.user
        if user.is_admin_user:
            return Order.objects.all()
        if user.is_courier:
            return Order.objects.filter(courier_assignment__courier=user)
        return Order.objects.filter(sender=user)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        order = self.object
        # Check if sender can leave a review
        ctx['can_review'] = (
            order.can_be_reviewed
            and self.request.user == order.sender
            and not hasattr(order, 'review')
        )
        # Progress steps for template
        ctx['progress_steps'] = [
            (s.value, s.label)
            for s in Order.Status
            if s not in (Order.Status.CANCELLED,)
        ]
        return ctx


class OrderCreateView(SenderRequiredMixin, CreateView):
    model         = Order
    form_class    = OrderForm
    template_name = 'orders/order_form.html'
    success_url   = reverse_lazy('orders:list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.sender = self.request.user
        response = super().form_valid(form)
        create_notification(
            user    = self.request.user,
            title   = 'Buyurtma qabul qilindi 📦',
            message = f'#{self.object.tracking_code} buyurtmangiz yaratildi. '
                      f'Narx: {self.object.price:,.0f} UZS'
        )
        messages.success(self.request, f'Buyurtma #{self.object.tracking_code} yaratildi!')
        return response


class MockPaymentView(LoginRequiredMixin, View):
    def get(self, request, pk):
        order = get_object_or_404(Order, pk=pk, sender=request.user)
        return render(request, 'orders/payment.html', {'order': order})

    def post(self, request, pk):
        order = get_object_or_404(Order, pk=pk, sender=request.user)
        order.is_paid = True
        order.save(update_fields=['is_paid'])
        create_notification(
            user    = request.user,
            title   = "To'lov tasdiqlandi ✅",
            message = f'#{order.tracking_code} buyurtma uchun to\'lov qabul qilindi.'
        )
        messages.success(request, "To'lov muvaffaqiyatli!")
        return redirect('orders:detail', pk=order.pk)


# ── Admin Dashboard ────────────────────────────────────────────────────────────
class AdminDashboardView(AdminRequiredMixin, TemplateView):
    template_name = 'orders/admin_dashboard.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        # Order stats
        ctx['total_orders']     = Order.objects.count()
        ctx['pending_orders']   = Order.objects.filter(status=Order.Status.PENDING).count()
        ctx['delivered_orders'] = Order.objects.filter(status=Order.Status.DELIVERED).count()
        ctx['unassigned_orders'] = Order.objects.filter(
            courier_assignment__isnull=True
        ).exclude(
            status__in=[Order.Status.DELIVERED, Order.Status.CANCELLED]
        ).select_related('sender', 'pickup_address')

        # Couriers with profile
        ctx['couriers'] = User.objects.filter(
            role=User.Role.COURIER
        ).select_related('courier_profile').prefetch_related('assignments')

        # Recent orders
        ctx['recent_orders'] = Order.objects.select_related(
            'sender', 'courier_assignment__courier'
        )[:20]

        return ctx


class AssignCourierView(AdminRequiredMixin, View):
    """Admin assigns a courier to an order."""

    def post(self, request, order_pk):
        order      = get_object_or_404(Order, pk=order_pk)
        courier_id = request.POST.get('courier_id')
        courier    = get_object_or_404(User, pk=courier_id, role=User.Role.COURIER)

        # Create or update assignment
        assignment, created = CourierAssignment.objects.update_or_create(
            order=order,
            defaults={'courier': courier, 'notes': request.POST.get('notes', '')}
        )

        create_notification(
            user    = courier,
            title   = 'Yangi yuk biriktirildi 🚚',
            message = f'#{order.tracking_code} buyurtma sizga biriktirildi.'
        )
        create_notification(
            user    = order.sender,
            title   = 'Kuryeringiz tayinlandi 👤',
            message = f'#{order.tracking_code} yukingizga kuryer tayinlandi: '
                      f'{courier.get_full_name() or courier.username}'
        )
        messages.success(request, f'Kuryer muvaffaqiyatli tayinlandi.')
        return redirect('orders:admin-dashboard')
