from django.contrib import admin
from .models import CustomUser,  Customer
from django.contrib.auth.admin import UserAdmin
from .forms import CustomUserCreationForm, CustomUserChangeForm


class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser
    list_display = ('email', 'role', 'is_active',)
    list_filter = ('email', 'role', 'is_active',)
    fieldsets = (
        (None, {'fields': ('first_name', 'last_name',
                           'email', 'password', 'email_verified')}),
        ('Permissions', {'fields': ('role',)}),
        ('Extra', {'fields': ('phone', 'gender', 'avatar')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'role', 'is_active')}
         ),
    )
    search_fields = ('email',)
    ordering = ('email',)


class HotelUserAdmin(admin.ModelAdmin):
    pass


# admin.site.register(HotelUser, HotelUserAdmin)

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Customer)
