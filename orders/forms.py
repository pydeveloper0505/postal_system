from django import forms
from .models import Order
from users.models import Address


class OrderForm(forms.ModelForm):
    class Meta:
        model  = Order
        fields = ('receiver_name', 'receiver_phone', 'receiver_email',
                  'pickup_address', 'delivery_address',
                  'weight', 'description', 'delivery_type')

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only show addresses belonging to this user
        user_addresses = Address.objects.filter(user=user)
        self.fields['pickup_address'].queryset   = user_addresses
        self.fields['delivery_address'].queryset = user_addresses
        self.fields['delivery_address'].required = False
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
        self.fields['delivery_type'].widget.attrs['class'] = 'form-select'

    def clean(self):
        cleaned = super().clean()
        dtype   = cleaned.get('delivery_type')
        daddr   = cleaned.get('delivery_address')
        if dtype == Order.DELIVERY_HOME and not daddr:
            raise forms.ValidationError('Home delivery requires a delivery address.')
        return cleaned
