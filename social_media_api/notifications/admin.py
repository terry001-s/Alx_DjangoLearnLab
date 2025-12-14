from django.contrib import admin
from .models import Notification, NotificationSettings

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['recipient', 'actor', 'verb', 'notification_type', 'is_read', 'created_at']
    list_filter = ['notification_type', 'is_read', 'created_at']
    search_fields = ['recipient__username', 'actor__username', 'verb']
    readonly_fields = ['created_at']
    list_per_page = 20
    
    fieldsets = [
        ('Basic Information', {
            'fields': ['recipient', 'actor', 'verb', 'notification_type']
        }),
        ('Target Object', {
            'fields': ['target_content_type', 'target_object_id'],
            'classes': ['collapse']
        }),
        ('Status', {
            'fields': ['is_read', 'created_at']
        }),
    ]

@admin.register(NotificationSettings)
class NotificationSettingsAdmin(admin.ModelAdmin):
    list_display = ['user', 'receive_like_notifications', 'receive_comment_notifications', 
                    'receive_follow_notifications', 'updated_at']
    list_filter = ['receive_like_notifications', 'receive_comment_notifications', 
                   'receive_follow_notifications']
    search_fields = ['user__username']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = [
        ('User', {
            'fields': ['user']
        }),
        ('Notification Preferences', {
            'fields': [
                'receive_like_notifications',
                'receive_comment_notifications',
                'receive_follow_notifications',
                'receive_mention_notifications'
            ]
        }),
        ('Email Preferences', {
            'fields': [
                'email_like_notifications',
                'email_comment_notifications',
                'email_follow_notifications'
            ],
            'classes': ['collapse']
        }),
        ('Timestamps', {
            'fields': ['created_at', 'updated_at'],
            'classes': ['collapse']
        }),
    ]