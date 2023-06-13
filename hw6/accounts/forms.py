from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, SetPasswordForm
from django.core.exceptions import ValidationError

from accounts.models import Profile
from accounts.validators import validate_birth_date

User = get_user_model()


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


class CreateProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('gender', 'date_of_birth', 'avatar', 'bio', 'info')


        widgets = {
            'avatar': forms.URLInput(),
            'date_of_birth': forms.DateInput(),
            'bio': forms.Textarea(),
            'info': forms.TextInput()
        }

    def __init__(self, *args, **kwargs):
        super(CreateProfileForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control border border-4 mb-3',
                                      'widgets': self.Meta.widgets.get(field_name)})
        self.fields['date_of_birth'].widget = CustomDateInput()

    def clean_date_of_birth(self):
        data = self.cleaned_data['date_of_birth']
        try:
            validate_birth_date(data)
        except ValidationError as error:
            self.add_error('date_of_birth', str(error))
        return data


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
