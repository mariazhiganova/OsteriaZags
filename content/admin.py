from django.contrib import admin

from content.models import ContentBlock


@admin.register(ContentBlock)
class ContentBlockAdmin(admin.ModelAdmin):
    list_display = ['slug', 'title', 'image']
    list_editable = ['title']
    search_fields = ['slug', 'title']
