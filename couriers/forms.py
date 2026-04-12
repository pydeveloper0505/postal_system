from django import forms
from orders.models import Order

# Maps current status → allowed next statuses
STATUS_TRANSITIONS = {
    Order.Status.PENDING:          [Order.Status.PICKED_UP, Order.Status.CANCELLED],
    Order.Status.PICKED_UP:        [Order.Status.IN_TRANSIT, Order.Status.CANCELLED],
    Order.Status.IN_TRANSIT:       [Order.Status.ARRIVED_BRANCH, Order.Status.CANCELLED],
    Order.Status.ARRIVED_BRANCH:   [Order.Status.OUT_FOR_DELIVERY],
    Order.Status.OUT_FOR_DELIVERY: [Order.Status.DELIVERED],
}


class UpdateStatusForm(forms.Form):
    status = forms.ChoiceField(choices=[])
    notes  = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        required=False,
        label='Izoh (ixtiyoriy)',
    )

    def __init__(self, order, *args, **kwargs):
        super().__init__(*args, **kwargs)
        allowed = STATUS_TRANSITIONS.get(order.status, [])
        self.fields['status'].choices = [
            (s.value, s.label)
            for s in Order.Status
            if s in allowed
        ]
        self.fields['status'].widget.attrs['class'] = 'form-select'
