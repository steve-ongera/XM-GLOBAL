from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext as _
from django.utils import timezone
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.crypto import get_random_string
from django.core.mail import send_mail
from django.conf import settings
import datetime

from .models import CustomUser, UserProfile, LoginAttempt, PasswordResetToken
from .forms import LoginForm, PasswordResetRequestForm, PasswordResetForm, SignupForm


def get_client_ip(request):
    """Helper function to get client IP address"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def login_view(request):
    """Handle user login"""
    if request.user.is_authenticated:
        return redirect('dashboard')
        
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')
            
            # Record login attempt
            login_attempt = LoginAttempt(
                email=email,
                ip_address=get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
            )
            
            user = authenticate(request, email=email, password=password)
            if user is not None:
                login(request, user)
                login_attempt.user = user
                login_attempt.successful = True
                login_attempt.save()
                
                # Update user's last login IP
                user.last_login_ip = get_client_ip(request)
                user.save()
                
                # Redirect to next parameter or dashboard
                next_url = request.GET.get('next', 'dashboard')
                return redirect(next_url)
            else:
                login_attempt.save()
                messages.error(request, _("Invalid email or password."))
    else:
        form = LoginForm()
        
    context = {
        'form': form,
    }
    return render(request, 'authentication/login.html', context)

def dashboard(request):
    return render (request , 'dashboard/dashboard.html')

def logout_view(request):
    """Handle user logout"""
    logout(request)
    messages.success(request, _("You have been successfully logged out."))
    return redirect('login')


def signup_view(request):
    """Handle user registration"""
    if request.user.is_authenticated:
        return redirect('dashboard')
        
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = True
            user.save()
            
            # Create user profile
            UserProfile.objects.create(user=user)
            
            # Log the user in
            login(request, user)
            
            messages.success(request, _("Account created successfully!"))
            return redirect('dashboard')
    else:
        form = SignupForm()
        
    context = {
        'form': form,
    }
    return render(request, 'authentication/signup.html', context)


def password_reset_request(request):
    """Handle password reset request"""
    if request.method == 'POST':
        form = PasswordResetRequestForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            try:
                user = CustomUser.objects.get(email=email)
                
                # Create a password reset token
                token = get_random_string(64)
                expiry = timezone.now() + datetime.timedelta(hours=24)
                
                PasswordResetToken.objects.create(
                    user=user,
                    token=token,
                    expires_at=expiry
                )
                
                # Send email with password reset link
                reset_link = request.build_absolute_uri(
                    reverse('password_reset_confirm', kwargs={'token': token})
                )
                
                send_mail(
                    subject=_("Password Reset Request"),
                    message=_(f"Click the link to reset your password: {reset_link}"),
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[email],
                    fail_silently=False,
                )
                
                messages.success(
                    request, 
                    _("Password reset link has been sent to your email.")
                )
                return redirect('login')
            except CustomUser.DoesNotExist:
                # For security, don't reveal whether a user exists
                messages.success(
                    request, 
                    _("If your email is registered, you will receive a password reset link.")
                )
                return redirect('login')
    else:
        form = PasswordResetRequestForm()
        
    context = {
        'form': form,
    }
    return render(request, 'authentication/password_reset_request.html', context)


def password_reset_confirm(request, token):
    """Handle password reset confirmation"""
    try:
        token_obj = PasswordResetToken.objects.get(token=token)
        
        if not token_obj.is_valid():
            messages.error(request, _("This password reset link has expired or been used."))
            return redirect('password_reset_request')
            
        if request.method == 'POST':
            form = PasswordResetForm(request.POST)
            if form.is_valid():
                user = token_obj.user
                user.set_password(form.cleaned_data.get('password'))
                user.save()
                
                # Mark token as used
                token_obj.used = True
                token_obj.save()
                
                messages.success(request, _("Your password has been reset successfully. Please log in."))
                return redirect('login')
        else:
            form = PasswordResetForm()
            
        context = {
            'form': form,
            'token': token
        }
        return render(request, 'authentication/password_reset_confirm.html', context)
        
    except PasswordResetToken.DoesNotExist:
        messages.error(request, _("Invalid password reset link."))
        return redirect('password_reset_request')


@login_required
def change_language(request):
    """Change user's preferred language"""
    if request.method == 'POST':
        language = request.POST.get('language', 'en')
        if hasattr(request.user, 'profile'):
            request.user.profile.preferred_language = language
            request.user.profile.save()
        
        # Set session language
        request.session['django_language'] = language
        
        # Redirect back to the referring page
        next_url = request.POST.get('next', request.META.get('HTTP_REFERER', 'dashboard'))
        return HttpResponseRedirect(next_url)
    
    return redirect('dashboard')