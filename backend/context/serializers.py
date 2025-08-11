from rest_framework import serializers
from .models import ContextEntry


class ContextEntrySerializer(serializers.ModelSerializer):
    def to_representation(self, instance):
        data = super().to_representation(instance)
        # derive naive insights if not stored
        content = (data.get('content') or '').lower()
        insights = data.get('processed_insights') or {}
        if not insights:
            insights = {
                'keywords': [k for k in ['meeting', 'deadline', 'follow up', 'email', 'shopping'] if k in content],
                'sentiment': 'negative' if any(b in content for b in ['issue', 'problem', 'delay']) else 'neutral',
            }
            data['processed_insights'] = insights
        return data
    class Meta:
        model = ContextEntry
        fields = [
            'id',
            'content',
            'source_type',
            'processed_insights',
            'created_at',
            'updated_at',
        ]


