from django.contrib import admin
from .models import ThrottlingMetrics

@admin.register(ThrottlingMetrics)
class ThrottlingMetricsAdmin(admin.ModelAdmin):
    list_display = ('user', 'daily_request_count', 'last_request_time')
    search_fields = ('user__username',)