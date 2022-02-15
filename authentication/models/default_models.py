from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from datetime import timedelta, datetime
from django.conf import settings
from authentication.constants import DEFAULT_AVATAR

from authentication.managers import CustomUserManager, CustomerManager, AllUserManager, HotelUserManager
from ..tasks import send_mail_asynchron

GENDER_CHOICES = (
    ('M', 'Male'),
    ('F', "Female"),
    ('O', "Other"),
    ('N', "No Information")
)


ROLE_CHOICES = (
    (0, 'Admin'),
    (1, 'HotelUser'),
    (2, 'Customer'),
)

class CustomUser(AbstractBaseUser, PermissionsMixin):    
    first_name = models.CharField(_('first name'), max_length=30, blank=True)
    last_name = models.CharField(_('last name'), max_length=150, blank=True)
    email = models.EmailField(_('email address'), unique=True)
    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_('Designates whether the user can log into this admin site.'),
    )
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ),
    )
    email_verified = models.BooleanField(default=False, verbose_name='email_activated')
    date_joined = models.DateTimeField(default=timezone.now)
    gender = models.CharField(choices=GENDER_CHOICES, max_length=1, default=GENDER_CHOICES[3][0])
    phone = models.CharField(max_length=15, null=True, blank=True)
    role = models.IntegerField(blank=True, default=ROLE_CHOICES[1][0], choices=ROLE_CHOICES)
    avatar = models.ImageField(upload_to='admin/avatar/', default=DEFAULT_AVATAR, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = AllUserManager()
    users = CustomUserManager()

    class Meta:
        verbose_name_plural = "Users"

    def __str__(self):
        return self.email

    def send_mail(self, **kwargs):
        kwargs['to_email'] = [self.email]
        send_mail_asynchron.delay(**kwargs)
        return "success"

    def save(self, *args, **kwargs):
        if(self.role == 2):
            pass
        elif(self.role == 0):
            self.role = 0
            self.is_staff = True
            self.is_superuser = True
        elif(self.role == 1):
            self.role = 1
            self.is_staff = False
            self.is_superuser = False
        super(CustomUser,self).save(*args, **kwargs)

    def delete(self):
        img_file = self.avatar
        if (not img_file.name == DEFAULT_AVATAR):
            img_file.delete()
        super().delete()

class Customer(CustomUser):
    objects = CustomerManager()
    dob = models.DateField(blank=True, null=True)


    class Meta:
        verbose_name_plural = "customers"

    def save(self, *args, **kwargs):
        self.role = 2
        self.is_staff = False
        self.is_superuser = False

        super(Customer,self).save(*args, **kwargs)


TOKEN_CHOICES = (
    (0, 'Registration'),
    (1, "Forget Password")
)

class UserToken(models.Model):
    key = models.CharField(max_length=80, unique=True)
    key_type = models.SmallIntegerField(choices=TOKEN_CHOICES)
    user = models.ForeignKey(to=CustomUser, related_name='user_token', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "UserTokens"

    def __str__(self):
        return self.key

    def isValid(self):
        if(self.key_type == 0):
            return (self.created_at + timedelta(days=250)) > datetime.now(self.created_at.tzinfo)
        elif(self.key_type == 1):
            return (self.created_at + timedelta(hours=1)) > datetime.now(self.created_at.tzinfo)
        else:
            return False
