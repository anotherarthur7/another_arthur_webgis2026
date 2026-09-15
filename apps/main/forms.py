# apps/main/forms.py
from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from apps.geo.models import City  # ← Add this

class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    password_confirm = forms.CharField(widget=forms.PasswordInput)
    email = forms.EmailField(required=True)
    user_type = forms.ChoiceField(
        choices=[
            ('consumer', 'Individual User'),
            ('business', 'Business Representative')
        ],
        widget=forms.RadioSelect,
        initial='consumer'
    )
    # ✅ ADD CITY FIELD
    city = forms.ModelChoiceField(
        queryset=City.objects.all(),
        empty_label="Select your city",
        required=True
    )

    class Meta:
        model = User
        fields = ('username', 'email')

    # ... your clean methods ...

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        user.is_active = False
        if commit:
            user.save()
            from apps.users.models import UserProfile
            UserProfile.objects.create(
                user=user,
                user_type=self.cleaned_data['user_type'],
                city=self.cleaned_data['city']  # ✅ Save city
            )
        return user