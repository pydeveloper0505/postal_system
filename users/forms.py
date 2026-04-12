from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User, Address
from .models import User, Address, CourierReview  # CourierReview qo'shildi

from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User, Address

class RegisterForm(UserCreationForm):
    email      = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=50, required=True)
    last_name  = forms.CharField(max_length=50, required=True)
    phone      = forms.CharField(max_length=20, required=False)
    role       = forms.ChoiceField(
        # BU YERDA O'ZGARIŞ: User.Role.SENDER va User.Role.COURIER deb yoziladi
        choices=[(User.Role.SENDER, 'Sender'), (User.Role.COURIER, 'Courier')]
    )

    class Meta:
        model  = User
        # password1 va password2 maydonlarini Meta dan olib tashlang
        fields = ('username', 'email', 'first_name', 'last_name', 'phone', 'role')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'

class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'


class ProfileForm(forms.ModelForm):
    class Meta:
        model  = User
        fields = ('first_name', 'last_name', 'email', 'phone', 'bio')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'


class AddressForm(forms.ModelForm):
    class Meta:
        model  = Address
        fields = ('title', 'region', 'city', 'street', 'house', 'zip_code', 'is_default')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
        self.fields['is_default'].widget.attrs['class'] = 'form-check-input'
class CourierReviewForm(forms.ModelForm):
    class Meta:
        model = CourierReview
        fields = ('score', 'comment')
        widgets = {
            'score': forms.NumberInput(attrs={'min': 1, 'max': 5}),
            'comment': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'