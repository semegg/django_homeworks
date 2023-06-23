from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, SetPasswordForm, PasswordChangeForm
from django.core.exceptions import ValidationError

from .models import Profile
from .validators import validate_birth_date

User = get_user_model()


class CustomDateInput(forms.DateInput):
    input_type = 'date'

    def __init__(self, attrs=None, options=None):
        if attrs is None:
            attrs = {}
        if options is None:
            options = {}
        attrs.update({'class': 'form-control mb-3', 'data-date-format': 'yyyy-mm-dd'})
        attrs.update(options)
        super().__init__(attrs=attrs)


class RegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(),
            'email': forms.EmailInput(),
            'first_name': forms.TextInput(),
            'last_name': forms.TextInput(),
            'password1': forms.PasswordInput(),
            'password2': forms.PasswordInput()
        }
        
    def __init__(self, *args, **kwargs):
        super(RegisterForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control mt-2 mb-2'})


class LoginForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    remember_me = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput({'class': 'form-check-input'})
    )


class BaseReactivationForm(forms.Form):
    email = forms.EmailField(label='Your email',
                             required=True,
                             widget=forms.EmailInput(attrs={'class': 'form-control'}))

    def clean_email(self):
        email = self.cleaned_data['email']
        user = User.objects.filter(email=email).first()
        if user is None:
            raise forms.ValidationError("User with this email doesn't exists")
        return email


class ReactivationForm(BaseReactivationForm):
    pass


class PasswordResetForm(BaseReactivationForm):
    pass


class PasswordSetForm(SetPasswordForm):
    class Meta:
        model = User
        fields = ["new_password1", "new_password2"]
        widgets = {
            'new_password1': forms.PasswordInput(),
            'new_password2': forms.PasswordInput(),
        }

    def __init__(self, *args, **kwargs):
        super(PasswordSetForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control mt-2 mb-2'})


class ChangePasswordForm(PasswordChangeForm):
    old_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control mb-4 mt-2', 'placeholder': 'Enter old password...'}),
        label='Old password'
    )
    new_password1 = forms.CharField(
            widget=forms.PasswordInput(attrs={'class': 'form-control mb-4 mt-2', 'placeholder': 'Enter new password...'}),
            label='New password'
        )
    new_password2 = forms.CharField(
            widget=forms.PasswordInput(attrs={'class': 'form-control mb-4 mt-2', 'placeholder': 'Conform new password...'}),
            label='Confirm new password'
        )

    def clean_new_password2(self):
        old_password = self.cleaned_data['old_password']
        new_password1 = self.cleaned_data['new_password1']
        new_password2 = self.cleaned_data['new_password2']

        if new_password1 == old_password:
            raise forms.ValidationError('The new password is the same as the old one.')

        if new_password1 != new_password2:
            raise forms.ValidationError('Two password fields did not match')
        return new_password2


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('gender', 'date_of_birth', 'avatar', 'bio', 'info')

        labels = {
            'date_of_birth': 'Date of your Birth',
            'avatar': 'Avatar URL'
        }

        placeholders = {
            'avatar': 'Left empty to use gravatar',
            'bio': 'Write short biography',
            'info': 'Enter some additional information'
        }

    def __init__(self, *args, **kwargs):
        super(ProfileForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control border border-4 mb-3',
                                      'placeholder': self.Meta.placeholders.get(field_name)})
        self.fields['date_of_birth'].widget = CustomDateInput()

    def clean_date_of_birth(self):
        data = self.cleaned_data['date_of_birth']
        try:
            validate_birth_date(data)
        except ValidationError as error:
            self.add_error('date_of_birth', str(error))
        return data

