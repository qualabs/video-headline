from rest_framework import serializers

from organization.models import Channel


class ChannelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Channel
        fields = (
            'id',
            'channel_id',
            'name',
            'allowed_domains',
            'ads_vast_url',
            'detect_adblock',
            'autoplay',
        )


class CreateChannelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Channel
        fields = (
            'name',
            'allowed_domains',
            'ads_vast_url',
            'detect_adblock',
            'autoplay',
        )


class MinChannelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Channel
        fields = ('id', 'channel_id', 'name', 'cf_domain')
