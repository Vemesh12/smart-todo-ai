from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import action
from .models import Task, Category
from .serializers import TaskSerializer, CategorySerializer
from context.models import ContextEntry
from context.serializers import ContextEntrySerializer
from .ai import suggest_tasks_and_priorities


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all().order_by("name")
    serializer_class = CategorySerializer


class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.select_related("category").all().order_by("-created_at")
    serializer_class = TaskSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        status_param = self.request.query_params.get("status")
        category_param = self.request.query_params.get("category")
        min_priority = self.request.query_params.get("min_priority")
        search = self.request.query_params.get("search")

        if status_param:
            qs = qs.filter(status=status_param)
        if category_param:
            qs = qs.filter(category_id=category_param)
        if min_priority:
            try:
                qs = qs.filter(priority_score__gte=float(min_priority))
            except ValueError:
                pass
        if search:
            qs = qs.filter(title__icontains=search) | qs.filter(description__icontains=search)
        return qs

    @staticmethod
    def _latest_context_payload(limit: int = 10):
        entries = ContextEntry.objects.order_by("-created_at").values("content", "source_type")[:limit]
        return list(entries)

    @action(detail=True, methods=["post"], url_path="ai-refresh")
    def ai_refresh(self, request, pk=None):
        task = self.get_object()
        context_payload = self._latest_context_payload()
        suggestions = suggest_tasks_and_priorities([
            {"title": task.title, "description": task.description}
        ], context_payload)
        s = (suggestions.get("suggestions") or [None])[0]
        if s:
            task.priority_score = s.get("suggested_priority_score", task.priority_score)
            from django.utils.dateparse import parse_datetime
            dl = s.get("suggested_deadline")
            if dl:
                task.deadline = parse_datetime(dl)
            cat_name = s.get("suggested_category_name")
            if cat_name:
                category, _ = Category.objects.get_or_create(name=cat_name)
                task.category = category
        task.save()
        serializer = self.get_serializer(task)
        return Response(serializer.data)


class AiSuggestView(APIView):
    def post(self, request):
        tasks_payload = request.data.get("tasks", [])
        context_payload = request.data.get("context", [])
        user_prefs = request.data.get("user_preferences", {})
        current_load = request.data.get("current_task_load", {})

        suggestions = suggest_tasks_and_priorities(
            tasks_payload,
            context_payload,
            user_preferences=user_prefs,
            current_task_load=current_load,
        )
        return Response(suggestions, status=status.HTTP_200_OK)

