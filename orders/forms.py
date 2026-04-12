from django import forms
from .models import Order
from users.models import Address


class OrderForm(forms.ModelForm):
    class Meta:
        model  = Order
        fields = ('receiver_name', 'receiver_phone', 'receiver_email',
                  'pickup_address', 'delivery_address',
                  'weight', 'description', 'delivery_type', 'is_insured')

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        user_addresses = Address.objects.filter(user=user)
        self.fields['pickup_address'].queryset   = user_addresses
        self.fields['delivery_address'].queryset = user_addresses
        self.fields['delivery_address'].required = False
        for name, field in self.fields.items():
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs['class'] = 'form-check-input'
            elif isinstance(field.widget, forms.Select):
                field.widget.attrs['class'] = 'form-select'
            else:
                field.widget.attrs['class'] = 'form-control'

    def clean(self):
        cleaned = super().clean()
        if (cleaned.get('delivery_type') == Order.DeliveryType.HOME
                and not cleaned.get('delivery_address')):
            raise forms.ValidationError(
                'Home delivery uchun yetkazish manzili kerak.'
            )
        return cleaned
