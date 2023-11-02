from django.contrib import admin, messages
from django.forms import ModelForm, forms
from django_fsm import TransitionNotAllowed

from video.models import Tag, Media, LiveVideo, LiveVideoCut


class VideoForm(ModelForm):
    class Meta:
        model = Media
        fields = '__all__'

    def clean(self):
        super(VideoForm, self).clean()

        # custom validation
        if self.cleaned_data.get('channels'):
            channels = self.cleaned_data.get('channels')
            organization = self.cleaned_data.get('organization')
            if len(channels) > 0:
                for chan in channels:
                    if chan not in organization.channels.all():
                        raise forms.ValidationError(
                            'One or more channels entered do not belong to your organization.'
                        )

        return self.cleaned_data


class LiveVideoForm(ModelForm):
    class Meta:
        model = LiveVideo
        fields = '__all__'

    def clean(self):
        super(LiveVideoForm, self).clean()

        # custom validation
        if self.cleaned_data.get('channels'):
            channels = self.cleaned_data.get('channels')
            organization = self.cleaned_data.get('organization')
            if len(channels) > 0:
                for chan in channels:
                    if chan not in organization.channels.all():
                        raise forms.ValidationError(
                            'One or more channels entered do not belong to your organization.'
                        )

        return self.cleaned_data


# Videos status functions for VOD
def change_video_status_to_queued(modeladmin, request, queryset):
    for video in queryset:
        try:
            video.to_queued()
        except TransitionNotAllowed:
            modeladmin.message_user(
                request,
                f'The status of the video {video.name} cannot be changed to the one entered.',
                level=messages.ERROR,
            )


def change_video_status_to_queued_failed(modeladmin, request, queryset):
    for video in queryset:
        try:
            video.to_queued_failed()
        except TransitionNotAllowed:
            modeladmin.message_user(
                request,
                f'The status of the video {video.name} cannot be changed to the one entered.',
                level=messages.ERROR,
            )


def change_video_status_to_processing(modeladmin, request, queryset):
    for video in queryset:
        try:
            video.to_processing()
        except TransitionNotAllowed:
            modeladmin.message_user(
                request,
                f'The status of the video {video.name} cannot be changed to the one entered.',
                level=messages.ERROR,
            )


def change_video_status_to_processing_failed(modeladmin, request, queryset):
    for video in queryset:
        try:
            video.to_processing_failed()
        except TransitionNotAllowed:
            modeladmin.message_user(
                request,
                f'The status of the video {video.name} cannot be changed to the one entered.',
                level=messages.ERROR,
            )


def change_video_status_to_finished(modeladmin, request, queryset):
    for video in queryset:
        try:
            video.to_finished()
        except TransitionNotAllowed:
            modeladmin.message_user(
                request,
                f'The status of the video {video.name} cannot be changed to the one entered.',
                level=messages.ERROR,
            )


def re_process_video(modeladmin, request, queryset):
    for video in queryset:
        try:
            video.re_process()
        except TransitionNotAllowed:
            modeladmin.message_user(
                request,
                f'The status of the video {video.name} cannot be changed to the one entered.',
                level=messages.ERROR,
            )


# Videos status function for live videos
def change_live_video_status_to_on(modeladmin, request, queryset):
    for video in queryset:
        try:
            video.to_on()
        except TransitionNotAllowed:
            modeladmin.message_user(
                request,
                f'The status of the live video {video.name} cannot be changed to the one entered.',
                level=messages.ERROR,
            )


def change_live_video_status_to_off(modeladmin, request, queryset):
    for video in queryset:
        try:
            video.to_off()
        except TransitionNotAllowed:
            modeladmin.message_user(
                request,
                f'The status of the live video {video.name} cannot be changed to the one entered.',
                level=messages.ERROR,
            )


def change_live_video_status_to_starting(modeladmin, request, queryset):
    for video in queryset:
        try:
            video.to_starting()
        except TransitionNotAllowed:
            modeladmin.message_user(
                request,
                f'The status of the live video {video.name} cannot be changed to the one entered.',
                level=messages.ERROR,
            )


def change_live_video_status_to_stopping(modeladmin, request, queryset):
    for video in queryset:
        try:
            video.to_stopping()
        except TransitionNotAllowed:
            modeladmin.message_user(
                request,
                f'The status of the live video {video.name} cannot be changed to the one entered.',
                level=messages.ERROR,
            )


# Videos status description for VOD
change_video_status_to_queued.short_description = 'Change status to Queued'
change_video_status_to_queued_failed.short_description = (
    'Change status to Queued (Failed)'
)
change_video_status_to_processing.short_description = 'Change status to Processing'
change_video_status_to_processing_failed.short_description = (
    'Change status to Processing (Failed)'
)
change_video_status_to_finished.short_description = 'Change status to Finished'
re_process_video.short_description = 'Re-process video'

# Video status description for live videos
change_live_video_status_to_on.short_description = 'Change status to On'
change_live_video_status_to_off.short_description = 'Change status to Off'
change_live_video_status_to_starting.short_description = 'Change status to Starting'
change_live_video_status_to_stopping.short_description = 'Change status to Stopping'


@admin.register(Media)
class VideoAdmin(admin.ModelAdmin):
    list_display = (
        'video_id',
        'name',
        'media_type',
        'organization',
        'created_by',
        'state',
        'created_at',
    )
    list_filter = (
        'organization',
        'state',
        'media_type',
    )
    search_fields = (
        'name',
        'organization__name',
        'video_id',
    )

    readonly_fields = (
        'video_id',
        'created_by',
        'state',
        'created_at',
        'has_thumbnail',
    )

    actions = [
        change_video_status_to_queued,
        change_video_status_to_queued_failed,
        change_video_status_to_processing,
        change_video_status_to_processing_failed,
        change_video_status_to_finished,
        re_process_video,
    ]
    form = VideoForm

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            # Only set added_by during the first save.
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = ['video_id', 'created_by', 'state', 'created_at']

        if obj is not None:
            readonly_fields.append('media_type')

        return readonly_fields


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'organization',
    )
    search_fields = ('name',)


@admin.register(LiveVideo)
class LiveVideoAdmin(admin.ModelAdmin):
    list_display = (
        'video_id',
        'name',
        'organization',
        'created_by',
        'state',
        'created_at',
    )
    list_filter = (
        'organization',
        'state',
    )
    search_fields = (
        'name',
        'organization__name',
        'video_id',
    )
    actions = [
        change_live_video_status_to_on,
        change_live_video_status_to_off,
        change_live_video_status_to_starting,
        change_live_video_status_to_stopping,
    ]
    form = LiveVideoForm

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            # Only set added_by during the first save.
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = [
            'video_id',
            'created_by',
            'state',
            'created_at',
        ]
        if obj is None:
            readonly_fields.append('geolocation_type')
            readonly_fields.append('geolocation_countries')

        return readonly_fields


@admin.register(LiveVideoCut)
class LiveVideoCutAdmin(admin.ModelAdmin):
    list_display = (
        'live',
        'initial_time',
        'final_time',
        'description',
        'created_by',
        'state',
    )

    readonly_fields = (
        'state',
        'created_by',
    )

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            # Only set added_by during the first save.
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
