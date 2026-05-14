from django import forms
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.core.exceptions import ValidationError
from .models import User
import re


class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, label='Пароль')
    password_confirm = forms.CharField(widget=forms.PasswordInput, label='Подтверждение пароля')
    
    class Meta:
        model = User
        fields = ['name', 'surname', 'email', 'phone']
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError('Пользователь с таким email уже существует')
        return email
    
    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if phone:
            digits = re.sub(r'\D', '', phone)
            if len(digits) == 11 and digits[0] == '8':
                phone = '+7' + digits[1:]
            elif len(digits) == 11 and digits.startswith('79'):
                phone = '+' + digits
            elif len(digits) == 12 and digits.startswith('7'):
                phone = '+' + digits
            else:
                raise ValidationError('Неверный формат номера телефона. Используйте 8XXXXXXXXXX или +7XXXXXXXXXX')
            
            if User.objects.filter(phone=phone).exists():
                raise ValidationError('Пользователь с таким номером телефона уже существует')
        return phone
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')
        if password and password_confirm and password != password_confirm:
            raise ValidationError('Пароли не совпадают')
        return cleaned_data


class UserLoginForm(AuthenticationForm):
    username = forms.EmailField(label='Email', widget=forms.EmailInput())
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput())
    
    error_messages = {
        'invalid_login': 'Неверный email или пароль',
    }


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['name', 'surname', 'avatar', 'about', 'phone', 'github_url']
    
    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if phone:
            digits = re.sub(r'\D', '', phone)
            if len(digits) == 11 and digits[0] == '8':
                phone = '+7' + digits[1:]
            elif len(digits) == 11 and digits.startswith('79'):
                phone = '+' + digits
            elif len(digits) == 12 and digits.startswith('7'):
                phone = '+' + digits
            else:
                raise ValidationError('Неверный формат номера телефона')
            
            if self.instance and self.instance.pk:
                if User.objects.filter(phone=phone).exclude(pk=self.instance.pk).exists():
                    raise ValidationError('Пользователь с таким номером телефона уже существует')
            else:
                if User.objects.filter(phone=phone).exists():
                    raise ValidationError('Пользователь с таким номером телефона уже существует')
        return phone
    
    def clean_github_url(self):
        url = self.cleaned_data.get('github_url')
        if url and not url.startswith('https://github.com/'):
            raise ValidationError('Ссылка должна вести на GitHub (https://github.com/...)')
        return url


class CustomPasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(label='Старый пароль', widget=forms.PasswordInput())
    new_password1 = forms.CharField(label='Новый пароль', widget=forms.PasswordInput())
    new_password2 = forms.CharField(label='Подтверждение пароля', widget=forms.PasswordInput())