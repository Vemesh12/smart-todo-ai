from django.db import models


class ContextEntry(models.Model):
    SOURCE_CHOICES = [
        ("whatsapp", "WhatsApp"),
        ("email", "Email"),
        ("note", "Note"),
        ("other", "Other"),
    ]

    content = models.TextField()
    source_type = models.CharField(max_length=20, choices=SOURCE_CHOICES)
    processed_insights = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"{self.source_type}: {self.content[:30]}..."

