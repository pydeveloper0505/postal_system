from django.views.generic import TemplateView, DetailView
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages

from .models import CourierAssignment
from .forms import UpdateStatusForm
from orders.models import Order
from users.mixins import CourierRequiredMixin
from notifications.utils import create_notification


class CourierDashboardView(CourierRequiredMixin, TemplateView):
    template_name = 'couriers/dashboard.html'

    # couriers/views.py

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        courier = self.request.user
        profile = getattr(courier, 'courier_profile', None)

        assignments = CourierAssignment.objects.filter(
            courier=courier
        ).select_related('order', 'order__sender', 'order__pickup_address')

        # 'order__is_active=True' qismini olib tashladik,
        # chunki status orqali filterlash yetarli:
        ctx['active_assignments'] = assignments.exclude(
            order__status__in=[Order.Status.DELIVERED, Order.Status.CANCELLED]
        )

        ctx['completed_assignments'] = assignments.filter(
            order__status=Order.Status.DELIVERED
        )

        ctx['profile'] = profile
        ctx['unassigned'] = Order.objects.filter(
            courier_assignment__isnull=True,
            status=Order.Status.PENDING,
        ).select_related('sender', 'pickup_address')[:10]

        return ctx

class UpdateOrderStatusView(CourierRequiredMixin, DetailView):
    template_name = 'couriers/update_status.html'

    def get_object(self):
        return get_object_or_404(
            CourierAssignment,
            pk=self.kwargs['pk'],
            courier=self.request.user
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['form'] = UpdateStatusForm(order=self.get_object().order)
        return ctx

    def post(self, request, *args, **kwargs):
        assignment = self.get_object()
        form = UpdateStatusForm(order=assignment.order, data=request.POST)
        if form.is_valid():
            old_status = assignment.order.status
            new_status = form.cleaned_data['status']
            assignment.order.status = new_status
            assignment.notes = form.cleaned_data.get('notes', '')
            assignment.order.save()   # ← triggers orders/signals.py
            assignment.save(update_fields=['notes'])

            messages.success(request, f'Status yangilandi: {new_status}')
            return redirect('couriers:dashboard')

        return self.render_to_response(self.get_context_data(form=form))
