from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Address


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display  = ('username', 'email', 'first_name', 'last_name', 'role', 'is_active')
    list_filter   = ('role', 'is_active', 'is_staff')
    search_fields = ('username', 'email', 'first_name', 'last_name', 'phone')
    ordering      = ('-date_joined',)

    fieldsets = UserAdmin.fieldsets + (
        ('Extra Info', {'fields': ('role', 'phone', 'bio')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Extra Info', {'fields': ('role', 'phone')}),
    )


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display  = ('user', 'title', 'city', 'street', 'is_default')
    list_filter   = ('city', 'is_default')
    search_fields = ('user__username', 'city', 'street')
