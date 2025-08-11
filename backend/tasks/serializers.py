from rest_framework import serializers
from .models import Task, Category


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = [
            'id',
            'name',
            'description',
            'usage_count',
            'created_at',
            'updated_at',
        ]


class TaskSerializer(serializers.ModelSerializer):
    category_detail = CategorySerializer(source='category', read_only=True)

    class Meta:
        model = Task
        fields = [
            'id',
            'title',
            'description',
            'category',
            'category_detail',
            'priority_score',
            'deadline',
            'status',
            'created_at',
            'updated_at',
        ]

    def create(self, validated_data):
        task = super().create(validated_data)
        category = task.category
        if category:
            category.usage_count = (category.usage_count or 0) + 1
            category.save(update_fields=["usage_count"])
        return task

    def update(self, instance, validated_data):
        old_category = instance.category
        task = super().update(instance, validated_data)
        new_category = task.category
        if old_category and old_category != new_category:
            old_category.usage_count = max((old_category.usage_count or 1) - 1, 0)
            old_category.save(update_fields=["usage_count"])
        if new_category and old_category != new_category:
            new_category.usage_count = (new_category.usage_count or 0) + 1
            new_category.save(update_fields=["usage_count"])
        return task


