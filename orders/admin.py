from django.contrib import admin
from .models import Order


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display  = ('tracking_code', 'sender', 'receiver_name', 'status',
                     'delivery_type', 'weight', 'price', 'is_paid', 'created_at')
    list_filter   = ('status', 'delivery_type', 'is_paid')
    search_fields = ('tracking_code', 'receiver_name', 'sender__username', 'sender__email')
    ordering      = ('-created_at',)
    list_editable = ('status', 'is_paid')
    readonly_fields = ('tracking_code', 'created_at', 'updated_at')

    fieldsets = (
        ('Order Info',   {'fields': ('tracking_code', 'sender', 'status', 'is_paid', 'price')}),
        ('Receiver',     {'fields': ('receiver_name', 'receiver_phone', 'receiver_email')}),
        ('Addresses',    {'fields': ('pickup_address', 'delivery_address', 'delivery_type')}),
        ('Parcel',       {'fields': ('weight', 'description')}),
        ('Timestamps',   {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)}),
    )
