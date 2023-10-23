import json
from django.core.exceptions import MultipleObjectsReturned
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from api.serializers import MinAccountSerializer, MinChannelSerializer
from api.serializers.tag import TagSerializer
from organization.models import Channel
from video.models import LiveVideo, Tag, LiveVideoCut


class LiveVideoSerializer(serializers.ModelSerializer):
    created_by = MinAccountSerializer()
    channel = MinChannelSerializer()
    tags = TagSerializer(many=True)
    actual_cut = serializers.SerializerMethodField()

    class Meta:
        model = LiveVideo
        fields = (
            'id',
            'video_id',
            'name',
            'created_by',
            'organization',
            'tags',
            'channel',
            'state',
            'input_state',
            'actual_cut',
            'ads_vast_url',
            'enable_ads',
            'created_at',
            'autoplay',
            'ml_input_url',
            'geolocation_type',
            'geolocation_countries'
        )

    def get_actual_cut(self, obj):
        from api.serializers import MinLiveVideoCutSerializer
        actual_cut = obj.cuts.filter(state=LiveVideoCut.State.EXECUTING).first()

        if actual_cut:
            return MinLiveVideoCutSerializer(actual_cut).data

        return None


class CreateLiveVideoSerializer(serializers.ModelSerializer):

    class Meta:
        model = LiveVideo
        fields = (
            'name',
            'channel',
            'tags',
            'ads_vast_url',
            'enable_ads',
            'autoplay',
            'geolocation_type',
            'geolocation_countries'        
        )


class UpdateLiveVideoSerializer(serializers.ModelSerializer):
    channel = serializers.PrimaryKeyRelatedField(queryset=Channel.objects)
    tags = serializers.ManyRelatedField(required=False, child_relation=serializers.CharField())

    class Meta:
        model = LiveVideo
        fields = (
            'name',
            'channel',
            'tags',
            'ads_vast_url',
            'enable_ads',
            'autoplay',
            'geolocation_type',
            'geolocation_countries'
        )

    def validate(self, data):
        request = self.context.get("request")
        try:
            user = request.user
        except AttributeError:
            raise ValidationError('You are not authenticated.')

        if data.get('tags'):
            tags_tmp = data.get('tags')
            if len(tags_tmp) > 0:
                tags_array = []
                for tag in tags_tmp:
                    try:
                        tag_object, created = Tag.objects.get_or_create(
                            name=tag,
                            organization=user.organization
                        )
                        tags_array.append(tag_object)
                    except MultipleObjectsReturned:
                        pass

                data['tags'] = tags_array
        if data.get('channel'):
            channel = data.get('channel')
            organization = user.organization
            if channel not in organization.channels.all():
                raise ValidationError('The channel does not belong to your organization.')
        else:
            raise ValidationError('The video must belong to a channel.')

        return data


class PartialUpdateLiveVideoSerializer(UpdateLiveVideoSerializer):
    channel = serializers.PrimaryKeyRelatedField(required=False, queryset=Channel.objects)

    def validate(self, data):
        request = self.context.get("request")
        try:
            user = request.user
        except AttributeError:
            raise ValidationError('You are not authenticated.')

        if data.get('tags'):
            tags_tmp = data.get('tags')
            if len(tags_tmp) > 0:
                tags_array = []
                for tag in tags_tmp:
                    try:
                        tag_object, created = Tag.objects.get_or_create(
                            name=tag,
                            organization=user.organization
                        )
                        tags_array.append(tag_object)
                    except MultipleObjectsReturned:
                        pass
                    
                data['tags'] = tags_array

        if data.get('channel'):
            channel = data.get('channel')
            organization = user.organization
            if channel not in organization.channels.all():
                raise ValidationError('The channel does not belong to your organization.')
        return data


class SubscribeSerializer(serializers.Serializer):
    video_id = serializers.CharField()
    endpoint_http = serializers.URLField()


class NotifySerializer(serializers.Serializer):
    Message = serializers.CharField(required=False, default=None)
    SubscribeURL = serializers.CharField(required=False, default=None)

    def validate_Message(self, data):
        request = self.context.get('request')
        is_notification = request.META.get('HTTP_X_AMZ_SNS_MESSAGE_TYPE') == 'Notification'

        if data and is_notification:
            return json.loads(data)
        return None