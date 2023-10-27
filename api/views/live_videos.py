import requests

from django.db import IntegrityError
from django_fsm import TransitionNotAllowed

from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.response import Response
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_201_CREATED
)
from rest_framework import permissions

from api.exceptions import SubscriptionError
from api.filters import LiveVideoFilter
from api.serializers import (
    LiveVideoSerializer,
    UpdateLiveVideoSerializer,
    PartialUpdateLiveVideoSerializer,
    CreateLiveVideoSerializer,
    SubscribeSerializer,
    NotifySerializer,
)
from utils import medialive, sns
from video.models import LiveVideo


class LiveVideoViewSet(viewsets.ModelViewSet):
    serializer_class = LiveVideoSerializer
    search_fields = (
        '=video_id',  # Exact field because of search filter
        'name',
        '=created_by__username',  # Exact field because of search filter
        'tags__name',
    )

    filterset_class = LiveVideoFilter

    def get_queryset(self):
        user = self.request.user

        return (
            LiveVideo.objects.select_related(
                'organization', 'channel', 'created_by'
            )
            .prefetch_related('tags')
            .filter(organization_id=user.organization_id)
            .order_by('-created_at')
        )

    def get_serializer_class(self):
        serializer_class = {
            'create': CreateLiveVideoSerializer,
            'update': UpdateLiveVideoSerializer,
            'partial_update': PartialUpdateLiveVideoSerializer,
            'subscribe': SubscribeSerializer,
            'notify': NotifySerializer,
        }

        if self.action and self.action in serializer_class.keys():
            return serializer_class[self.action]
        else:
            return self.serializer_class

    def get_permissions(self):
        permission_classes = {
            'create': [permissions.IsAdminUser],
            'destroy': [permissions.IsAdminUser],
        }

        if self.action and self.action in permission_classes.keys():
            self.permission_classes = permission_classes[self.action]

        return super(LiveVideoViewSet, self).get_permissions()

    def create(self, request, *args, **kwargs):
        input_serializer = self.get_serializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)

        user = self.request.user
        organization = user.organization

        try:
            live = LiveVideo.objects.create(
                created_by=user,
                organization=organization,
                **input_serializer.validated_data
            )

        except IntegrityError:
            raise ValidationError(
                {'non_field_errors': ['Error while creating live video.']}
            )

        data = LiveVideoSerializer(live).data

        return Response(data, status=HTTP_201_CREATED)

    # DELETE /live-videos/{id}/to_delete
    @action(detail=True, methods=['delete'])
    def to_delete(self, request, **kwargs):
        try:
            live = self.get_object()
            live.to_deleting()
        except Exception:
            raise ValidationError(
                {'non_field_errors': ['Error while deleting live video.']}
            )
        return Response(status=HTTP_200_OK)

    # POST /live-videos/{id}/to_on
    @action(detail=True, methods=['post'])
    def to_on(self, request, **kwargs):
        live = self.get_object()

        if live.state != LiveVideo.State.STARTING:
            try:
                live.to_starting()
            except TransitionNotAllowed:
                raise ValidationError(
                    {
                        'non_field_errors': [
                            'Cannot be changed to the entered state.'
                        ]
                    }
                )
            except medialive.ChannelNotFoundException:
                raise NotFound(
                    detail=('There was an internal problem,'
                            'contact yourAdministrator.')
                )

        return Response()

    # POST /live-videos/{id}/to_off
    @action(detail=True, methods=['post'])
    def to_off(self, request, **kwargs):
        live = self.get_object()
        if live.state != LiveVideo.State.STOPPING:
            try:
                live.to_stopping()
            except TransitionNotAllowed:
                raise ValidationError(
                    {
                        'non_field_errors': [
                            'Cannot be changed to the entered state.'
                        ]
                    }
                )
            except medialive.ChannelNotFoundException:
                raise NotFound(
                    detail=('There was an internal problem,'
                            'contact your Administrator.')
                )

        return Response()

    # POST /live-videos/subscribe/
    @action(detail=False, methods=['post'])
    def subscribe(self, request, **kwargs):
        input_serializer = self.get_serializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)

        try:
            live = self.get_queryset().get(
                video_id=input_serializer.validated_data['video_id']
            )

            arn = sns.subscribe(
                live, input_serializer.validated_data['endpoint_http']
            )

            data = {'subscription_id': arn, 'channel_arn': live.ml_channel_arn}

            return Response(data)
        except LiveVideo.DoesNotExist:
            raise NotFound(detail='Live Video not found.')
        except sns.NotificationNotFoundException:
            raise SubscriptionError()

    # POST /live-videos/notify
    @action(
        detail=False,
        methods=['post'],
        permission_classes=[permissions.AllowAny],
    )
    def notify(self, request, **kwargs):
        input_serializer = self.get_serializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)

        if input_serializer.validated_data['SubscribeURL']:
            # Confirm subscription to topic
            requests.get(input_serializer.validated_data['SubscribeURL'])
        else:
            # subscription already confirmed
            msg = input_serializer.validated_data['Message']

            medialive.add_channel_alert(msg)

        return Response()
