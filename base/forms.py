from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.utils.translation import gettext_lazy as _
from .models import CustomUser


class LoginForm(forms.Form):
    """Form for user login"""
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'email-input', 
            'placeholder': 'Email'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'password-input', 
            'placeholder': 'Password'
        })
    )


class SignupForm(UserCreationForm):
    """Form for user registration"""
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'email-input', 
            'placeholder': 'Email'
        })
    )
    
    class Meta:
        model = CustomUser
        fields = ('email', 'username', 'password1', 'password2')
        
    def __init__(self, *args, **kwargs):
        super(SignupForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'class': 'username-input',
            'placeholder': 'Username'
        })
        self.fields['password1'].widget.attrs.update({
            'class': 'password-input',
            'placeholder': 'Password'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'password-input',
            'placeholder': 'Confirm Password'
        })
        
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError(_("This email is already in use."))
        return email


class PasswordResetRequestForm(forms.Form):
    """Form for requesting a password reset"""
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'email-input', 
            'placeholder': 'Email'
        })
    )


class PasswordResetForm(forms.Form):
    """Form for resetting password"""
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'password-input', 
            'placeholder': 'New Password'
        }),
        min_length=8
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'password-input', 
            'placeholder': 'Confirm New Password'
        })
    )
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        
        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError(_("Passwords don't match."))
            
        return cleaned_data