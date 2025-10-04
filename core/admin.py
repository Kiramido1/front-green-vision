from django.contrib import admin
from .models import ContactMessage, NewsletterSubscriber, MapLocation


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'subject', 'created_at', 'is_read']
    list_filter = ['is_read', 'created_at']
    search_fields = ['name', 'email', 'subject', 'message']
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'
    
    def mark_as_read(self, request, queryset):
        queryset.update(is_read=True)
    mark_as_read.short_description = "Mark selected messages as read"
    
    actions = [mark_as_read]


@admin.register(NewsletterSubscriber)
class NewsletterSubscriberAdmin(admin.ModelAdmin):
    list_display = ['email', 'subscribed_at', 'is_active']
    list_filter = ['is_active', 'subscribed_at']
    search_fields = ['email']
    readonly_fields = ['subscribed_at']
    date_hierarchy = 'subscribed_at'


@admin.register(MapLocation)
class MapLocationAdmin(admin.ModelAdmin):
    list_display = ['country', 'city', 'latitude', 'longitude', 'crop_yield', 'soil_health', 'efficiency']
    list_filter = ['country', 'created_at']
    search_fields = ['country', 'city', 'description']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('Location Information', {
            'fields': ('country', 'city', 'latitude', 'longitude', 'description')
        }),
        ('Agricultural Data', {
            'fields': ('crop_yield', 'soil_health', 'efficiency')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
