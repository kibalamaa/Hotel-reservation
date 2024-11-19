from django.contrib import admin

from .models import ChatMessage

# Register the ChatMessage model with the admin site
@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('sender', 'recipient', 'message', 'timestamp', 'status')
    list_filter = ('status', 'sender', 'recipient')  # Optional: Filters for easier management
    search_fields = ('message', 'sender__username', 'recipient__username')  # Optional: Allows searching
