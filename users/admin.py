from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Address, CourierProfile, CourierReview


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display  = ('username', 'email', 'get_full_name', 'role', 'is_active', 'date_joined')
    list_filter   = ('role', 'is_active', 'is_staff')
    search_fields = ('username', 'email', 'first_name', 'last_name', 'phone')
    ordering      = ('-date_joined',)
    fieldsets     = UserAdmin.fieldsets + (
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


@admin.register(CourierProfile)
class CourierProfileAdmin(admin.ModelAdmin):
    list_display  = ('courier', 'status', 'rating', 'active_orders_count',
                     'delivered_count', 'total_assigned_count', 'is_available')
    list_filter   = ('status', 'is_available')
    search_fields = ('courier__username',)
    readonly_fields = ('rating', 'total_reviews', 'active_orders_count',
                       'delivered_count', 'total_assigned_count')


@admin.register(CourierReview)
class CourierReviewAdmin(admin.ModelAdmin):
    list_display  = ('courier', 'sender', 'score', 'created_at')
    list_filter   = ('score',)
    search_fields = ('courier__username', 'sender__username')
    readonly_fields = ('created_at',)
