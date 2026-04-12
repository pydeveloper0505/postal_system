from django import forms
from orders.models import Order


STATUS_NEXT = {
    Order.STATUS_PENDING:          Order.STATUS_PICKED_UP,
    Order.STATUS_PICKED_UP:        Order.STATUS_IN_TRANSIT,
    Order.STATUS_IN_TRANSIT:       Order.STATUS_ARRIVED_BRANCH,
    Order.STATUS_ARRIVED_BRANCH:   Order.STATUS_OUT_FOR_DELIVERY,
    Order.STATUS_OUT_FOR_DELIVERY: Order.STATUS_DELIVERED,
}

ALLOWED_STATUSES = list(STATUS_NEXT.values()) + [Order.STATUS_CANCELLED]


class UpdateStatusForm(forms.Form):
    status = forms.ChoiceField(choices=Order.STATUS_CHOICES)
    notes  = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}), required=False)

    def __init__(self, order, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only show next logical status + cancelled
        next_status = STATUS_NEXT.get(order.status)
        available = [(s, l) for s, l in Order.STATUS_CHOICES
                     if s in (next_status, Order.STATUS_CANCELLED) and next_status]
        self.fields['status'].choices = available or Order.STATUS_CHOICES
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
