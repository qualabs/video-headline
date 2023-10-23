from django_filters import rest_framework as filters

from video.models import Media, LiveVideo, LiveVideoCut


class MediaFilter(filters.FilterSet):
    NOT_FINISHED = (Media.State.NOT_FINISHED, Media.State.NOT_FINISHED)
    FAILED = (Media.State.FAILED, Media.State.FAILED)
    state_choices = Media.State.CHOICES + (NOT_FINISHED, FAILED)

    state = filters.MultipleChoiceFilter(choices=state_choices, method='state_filter')
    tags = filters.CharFilter(method='tags_filter')
    video_ids = filters.CharFilter(method='video_ids_filter')

    class Meta:
        model = Media
        fields = (
            'channel__name',
            'channel__id',
            'tags__name',
            'tags__id',
            'created_by__username',
            'state',
            'tags',
            'video_id',
            'media_type'
        )

    def tags_filter(self, queryset, value, *args, **kwargs):
        tags_list = args[0].split(',')

        for tag in tags_list:
            queryset = queryset.filter(tags__name=tag)

        return queryset

    def video_ids_filter(self, queryset, value, *args, **kwargs):
        video_ids_list = args[0].split(",")
        queryset = queryset.filter(video_id__in=video_ids_list)

        return queryset

    def state_filter(self, queryset, name, value):
        not_finised = [Media.State.PROCESSING, Media.State.WAITING_FILE, Media.State.QUEUED]
        failed = [Media.State.PROCESSING_FAILED, Media.State.QUEUING_FAILED]

        for state_filter in value:
            if (state_filter == Media.State.NOT_FINISHED):
                value.extend(not_finised)
            elif (state_filter == Media.State.FAILED):
                value.extend(failed)

        queryset = queryset.filter(state__in=value)
        return queryset


class LiveVideoFilter(filters.FilterSet):
    state = filters.MultipleChoiceFilter(choices=LiveVideo.State.CHOICES, method='state_filter')
    tags = filters.CharFilter(method='tags_filter')

    class Meta:
        model = LiveVideo
        fields = (
            'channel__name',
            'channel__id',
            'tags__name',
            'tags__id',
            'created_by__username',
            'state',
            'tags'
        )

    def tags_filter(self, queryset, value, *args, **kwargs):
        tags_list = args[0].split(',')

        for tag in tags_list:
            queryset = queryset.filter(tags__name=tag)

        return queryset

    def state_filter(self, queryset, name, value):
        queryset = queryset.filter(state__in=value)
        return queryset


class LiveVideoCutsFilter(filters.FilterSet):
    state = filters.MultipleChoiceFilter(choices=LiveVideoCut.State.CHOICES, method='state_filter')

    class Meta:
        model = LiveVideoCut
        fields = (
            'live_id',
            'live__video_id',
            'created_by__username',
            'state'
        )

    def state_filter(self, queryset, name, value):
        queryset = queryset.filter(state__in=value)
        return queryset
