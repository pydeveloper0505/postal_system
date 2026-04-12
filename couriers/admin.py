from django.contrib import admin
from .models import CourierAssignment


@admin.register(CourierAssignment)
class CourierAssignmentAdmin(admin.ModelAdmin):
    list_display  = ('courier', 'order', 'assigned_at')
    list_filter   = ('courier',)
    search_fields = ('courier__username', 'order__tracking_code')
    raw_id_fields = ('courier', 'order')
    readonly_fields = ('assigned_at',)
