from django.views.generic import ListView, DetailView, FormView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.urls import reverse

from .models import CourierAssignment
from .decorators import CourierRequiredMixin
from .forms import UpdateStatusForm
from orders.models import Order
from notifications.utils import create_notification


class CourierDashboardView(CourierRequiredMixin, TemplateView):
    template_name = 'couriers/dashboard.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        courier = self.request.user
        assignments = CourierAssignment.objects.filter(
            courier=courier
        ).select_related('order', 'order__sender', 'order__pickup_address')

        ctx['active_assignments'] = assignments.exclude(
            order__status__in=[Order.STATUS_DELIVERED, Order.STATUS_CANCELLED]
        )
        ctx['completed_assignments'] = assignments.filter(
            order__status=Order.STATUS_DELIVERED
        )
        ctx['total_delivered'] = ctx['completed_assignments'].count()
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
            new_status = form.cleaned_data['status']
            notes      = form.cleaned_data.get('notes', '')

            old_status = assignment.order.status
            assignment.order.status = new_status
            assignment.notes = notes
            assignment.order.save()
            assignment.save()

            # Notify sender
            create_notification(
                user    = assignment.order.sender,
                title   = 'Parcel status updated',
                message = f'Order #{assignment.order.tracking_code} status changed from '
                          f'"{old_status}" to "{new_status}".'
            )

            messages.success(request, f'Status updated to {new_status}.')
            return redirect('couriers:dashboard')

        return self.render_to_response(self.get_context_data(form=form))
