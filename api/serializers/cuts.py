from rest_framework import serializers
from rest_framework.exceptions import NotAuthenticated, PermissionDenied

from api.serializers import MinAccountSerializer
from video.models.cuts import LiveVideoCut, LiveVideo


class MinLiveVideoCutSerializer(serializers.ModelSerializer):
    class Meta:
        model = LiveVideoCut
        fields = (
            'id',
            'final_time',
            'description',
        )


class LiveVideoCutSerializer(serializers.ModelSerializer):
    created_by = MinAccountSerializer()

    class Meta:
        model = LiveVideoCut
        fields = (
            'id',
            'live',
            'initial_time',
            'final_time',
            'description',
            'created_by',
            'state'
        )


class CreateLiveVideoCutSerializer(serializers.ModelSerializer):
    live = serializers.PrimaryKeyRelatedField(queryset=LiveVideo.objects)
    description = serializers.CharField(max_length=200, required=True)

    class Meta:
        model = LiveVideoCut
        fields = (
            'live',
            'initial_time',
            'final_time',
            'description',
            'created_by'
        )
        extra_kwargs = {'created_by': {'read_only': True}}

    def validate_live(self, live_video):
        request = self.context.get("request")
        try:
            user = request.user
        except AttributeError:
            raise NotAuthenticated()

        if live_video.organization == user.organization:
            return live_video

        raise PermissionDenied()


class UpdateLiveVideoCutSerializer(serializers.ModelSerializer):
    class Meta:
        model = LiveVideoCut
        fields = (
            'initial_time',
            'final_time',
            'description',
        )
