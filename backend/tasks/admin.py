from django.contrib import admin
from .models import Task, Category


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "usage_count", "created_at", "updated_at")
    search_fields = ("name",)


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "category",
        "priority_score",
        "deadline",
        "status",
        "created_at",
        "updated_at",
    )
    list_filter = ("status", "category")
    search_fields = ("title", "description")

