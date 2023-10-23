import re
from django.core.exceptions import MultipleObjectsReturned
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from api.serializers import MinAccountSerializer, MinChannelSerializer
from api.serializers.tag import TagSerializer
from organization.models import Channel
from video.models import Media, Tag


class MediaSerializer(serializers.ModelSerializer):
    created_by = MinAccountSerializer()
    channel = MinChannelSerializer()
    tags = TagSerializer(many=True)
    job_percent_complete = serializers.SerializerMethodField()
    thumbnail_url = serializers.SerializerMethodField()
    media_url = serializers.SerializerMethodField()

    class Meta:
        model = Media
        fields = (
            'id',
            'video_id',
            'name',
            'created_by',
            'organization',
            'tags',
            'channel',
            'state',
            'ads_vast_url',
            'enable_ads',
            'autoplay',
            'created_at',
            'media_type',
            'job_percent_complete',
            'has_thumbnail',
            'thumbnail_url',
            'media_url',
        )

    def get_job_percent_complete(self, obj):
        job_percent_complete = obj.metadata.get('job_percent_complete', None)
        return job_percent_complete

    def get_thumbnail_url(self, obj):
        poster, _, _ = obj.get_urls()
        return poster

    def get_media_url(self, obj):
        _, media_url, _ = obj.get_urls()
        return media_url

class CreateMediaSerializer(serializers.ModelSerializer):
    content_type = serializers.CharField(required=True)
    video_id = serializers.CharField(required=False)
    channel_id = serializers.PrimaryKeyRelatedField(queryset=Channel.objects, required=False, default=None)

    class Meta:
        model = Media
        fields = (
            'name',
            'content_type',
            'video_id',
            'media_type',
            'channel_id',
        )

    def validate_channel_id(self, data):
        if data:
            request = self.context.get("request")

            try:
                user = request.user
            except AttributeError:
                raise ValidationError('You are not authenticated.')

            organization = user.organization
            if data not in organization.channels.all():
                raise ValidationError('The channel does not belong to your organization.')

        return data

    def validate_content_type(self, data):
        pattern = r'^video/(.*)$'
        error_message = 'Only video files are allowed to be uploaded.'

        audio_pattern = r'^audio/(.*)$'

        if re.match(audio_pattern, data):
            pattern = audio_pattern
            error_message = 'Only audio files are allowed to be uploaded.'

        if not re.match(pattern, data):
            raise ValidationError(error_message)

        return data


class UpdateMediaSerializer(serializers.ModelSerializer):
    channel = serializers.PrimaryKeyRelatedField(queryset=Channel.objects)
    tags = serializers.ManyRelatedField(
        required=False,
        child_relation=serializers.CharField()
    )

    class Meta:
        model = Media
        fields = (
            'name',
            'channel',
            'tags',
            'ads_vast_url',
            'enable_ads',
            'autoplay',
            'has_thumbnail'
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


class PartialUpdateMediaSerializer(UpdateMediaSerializer):
    channel = serializers.PrimaryKeyRelatedField(required=False,
                                                 queryset=Channel.objects)

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


class ThumbnailMediaSerializer (serializers.Serializer):
    content_type = serializers.CharField(required=True)
