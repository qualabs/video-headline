from rest_framework import serializers

from organization.models import Bill, Plan


class PlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plan
        fields = (
            'id',
            'name',
            'video_transcoding',
            'audio_transcoding',
            'storage',
            'data_transfer',
        )


class BillSerializer(serializers.ModelSerializer):
    plan = PlanSerializer()
    extras = serializers.JSONField()

    class Meta:
        model = Bill
        fields = (
            'id',
            'organization',
            'plan',
            'date',
            'last_modified',
            'video_transcoding',
            'audio_transcoding',
            'storage',
            'data_transfer',
            'extras',
        )


class MinBillSerializer(serializers.ModelSerializer):
    plan = serializers.CharField(source='plan.name')

    class Meta:
        model = Bill
        fields = ('id', 'plan', 'date')
