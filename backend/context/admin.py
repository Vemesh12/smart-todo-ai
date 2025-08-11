from django.contrib import admin
from .models import ContextEntry


@admin.register(ContextEntry)
class ContextEntryAdmin(admin.ModelAdmin):
    list_display = ("source_type", "created_at", "updated_at")
    list_filter = ("source_type",)
    search_fields = ("content",)

