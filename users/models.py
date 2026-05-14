import uuid

from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.core.validators import RegexValidator

from .avatar_generate import build_registration_avatar_png


class UserManager(BaseUserManager):
    def create_user(self, email, name, surname, phone, password=None, **extra_fields):
        if not email:
            raise ValueError('Email обязателен')
        email = self.normalize_email(email)
        user = self.model(
            email=email,
            name=name,
            surname=surname,
            phone=phone,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, surname, phone, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        return self.create_user(email, name, surname, phone, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True, verbose_name='Email')
    name = models.CharField(max_length=124, verbose_name='Имя')
    surname = models.CharField(max_length=124, verbose_name='Фамилия')
    avatar = models.ImageField(upload_to='avatars/', verbose_name='Аватар', blank=True, null=True)
    phone = models.CharField(
        max_length=12,
        validators=[RegexValidator(r'^\+7\d{10}$', message='Номер должен быть в формате +7XXXXXXXXXX')],
        unique=True,
        verbose_name='Телефон'
    )
    github_url = models.URLField(blank=True, null=True, verbose_name='GitHub')
    about = models.TextField(max_length=256, blank=True, null=True, verbose_name='О себе')
    
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Для варианта 1: избранные проекты
    favorites = models.ManyToManyField('projects.Project', blank=True, related_name='favorited_by', verbose_name='Избранные проекты')
    
    objects = UserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name', 'surname', 'phone']
    
    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
    
    def __str__(self):
        return f'{self.name} {self.surname}'
    
    def get_full_name(self):
        return f'{self.name} {self.surname}'

    def save(self, *args, **kwargs):
        if self._state.adding and not self.avatar and (self.name or "").strip():
            avatar_file = build_registration_avatar_png(self.name)
            filename = f"avatar_{uuid.uuid4().hex}.png"
            self.avatar.save(filename, avatar_file, save=False)
        super().save(*args, **kwargs)