from rest_framework import viewsets
from .models import ContextEntry
from .serializers import ContextEntrySerializer
from rest_framework.response import Response
from rest_framework.decorators import action


class ContextEntryViewSet(viewsets.ModelViewSet):
    queryset = ContextEntry.objects.all().order_by("-created_at")
    serializer_class = ContextEntrySerializer

    @action(detail=False, methods=["get"], url_path="latest")
    def latest(self, request):
        qs = self.get_queryset()[:10]
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)

