from rest_framework import serializers

from organization.models import Organization, AWSAccount


class AWSAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = AWSAccount
        fields = (
            'access_key',
            'region',
        )


class OrganizationSerializer(serializers.ModelSerializer):
    config = serializers.JSONField()
    aws_account = AWSAccountSerializer()

    class Meta:
        model = Organization
        fields = (
            'id',
            'name',
            'config',
            'upload_enabled',
            'traffic_enabled',
            'security_enabled',
            'aws_account',
            'bucket_name',
            'cf_distribution_ids'
            )
