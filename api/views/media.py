import hmac

import datetime
import hashlib
from django.db import IntegrityError
from django.http import HttpResponse
from django_fsm import TransitionNotAllowed
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.status import HTTP_201_CREATED, HTTP_200_OK
from rest_framework.status import HTTP_400_BAD_REQUEST

from api.filters import MediaFilter
from api.serializers import MediaSerializer, CreateMediaSerializer, UpdateMediaSerializer, \
    PartialUpdateMediaSerializer, ThumbnailMediaSerializer
from utils.cloudfront import create_invalidation
from utils.s3 import get_put_presigned_s3_url, delete_object, get_signature_key
from video.models import Media


class MediaViewSet(viewsets.ModelViewSet):
    serializer_class = MediaSerializer
    search_fields = (
        'video_id',
        'name',
        'created_by__username',
        'tags__name'
    )
    filterset_class = MediaFilter

    def get_queryset(self):
        user = self.request.user

        return Media.objects.select_related('organization', 'channel',
                                            'created_by').prefetch_related('tags').filter(
            organization_id=user.organization_id).order_by('-created_at')

    def get_serializer_class(self):
        serializer_class = {
            'create': CreateMediaSerializer,
            'update': UpdateMediaSerializer,
            'partial_update': PartialUpdateMediaSerializer,
            'thumbnail': ThumbnailMediaSerializer
        }

        if self.action and self.action in serializer_class.keys():
            return serializer_class[self.action]

        else:
            return self.serializer_class

    def create(self, request, *args, **kwargs):
        input_serializer = self.get_serializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)

        user = self.request.user
        organization = user.organization

        if not organization.upload_enabled:
            raise PermissionDenied()

        content_type = input_serializer.validated_data.pop('content_type')
        channel_id = input_serializer.validated_data.pop('channel_id')

        try:
            media = Media.objects.create(
                created_by=user,
                organization=organization,
                **input_serializer.validated_data
            )
        except IntegrityError:
            raise ValidationError({'non_field_errors': ['Error creating video.']})

        if channel_id:
            media.channel = channel_id
            media.save()

        signed_url = get_put_presigned_s3_url(organization, f'{media.video_id}/input.mp4',
                                              content_type)
        data = {
            'signed_url': signed_url
        }

        data.update(MediaSerializer(media).data)

        return Response(data, status=HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def to_queued(self, request, **kwargs):
        media = self.get_object()

        try:
            media.to_queued()
        except TransitionNotAllowed:
            raise ValidationError(
                {'non_field_errors': ['Cannot be changed to the entered state.']})

        return Response(HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def to_queued_failed(self, request, **kwargs):
        media = self.get_object()

        try:
            media.to_queued_failed()
        except TransitionNotAllowed:
            raise ValidationError(
                {'non_field_errors': ['Cannot be changed to the entered state.']})

        return Response(HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def to_processing(self, request, **kwargs):
        media = self.get_object()

        try:
            media.to_processing()
        except TransitionNotAllowed:
            raise ValidationError(
                {'non_field_errors': ['Cannot be changed to the entered state.']})

        return Response(HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def to_processing_failed(self, request, **kwargs):
        media = self.get_object()

        try:
            media.to_processing_failed()
        except TransitionNotAllowed:
            raise ValidationError(
                {'non_field_errors': ['Cannot be changed to the entered state.']})

        return Response(HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def to_finished(self, request, **kwargs):
        media = self.get_object()

        try:
            media.to_finished()
        except TransitionNotAllowed:
            raise ValidationError(
                {'non_field_errors': ['Cannot be changed to the entered state.']})

        return Response(HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def signature(self, request, **kwargs):
        organization = request.user.organization

        to_sign = str(request.GET.get('to_sign')).encode('utf-8')

        date_stamp = datetime.datetime.strptime(request.GET.get('datetime'),
                                                '%Y%m%dT%H%M%SZ').strftime('%Y%m%d')

        aws_secret = organization.aws_account.secret_access_key
        region = organization.aws_account.region

        signing_key = get_signature_key(aws_secret, date_stamp, region, 's3')

        # Sign to_sign using the signing_key
        signature = hmac.new(
            signing_key,
            to_sign,
            hashlib.sha256
        ).hexdigest()

        return HttpResponse(signature)

    @action(detail=True, methods=['post', 'delete'])
    def thumbnail(self, request, **kwargs):
        if request.method == 'DELETE':
            return self._delete_thumbnail(request, **kwargs)
        else:
            return self._thumbnail_signed_url(request, **kwargs)

    def _thumbnail_signed_url(self, request, **kwargs):
        input_serializer = self.get_serializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)

        media = self.get_object()

        content_type = input_serializer.validated_data.pop('content_type')
        signed_url = get_put_presigned_s3_url(media.organization, f'{media.video_id}/thumb.jpg',
                                              content_type, 'public-read')

        # Invalidate cache on CloudFront
        create_invalidation(media.organization, media.channel.cf_id, [
            '/{}/thumb.jpg'.format(media.video_id)
        ])

        data = {
            'signed_url': signed_url
        }

        return Response(data, status=HTTP_200_OK)

    def _delete_thumbnail(self, request, **kwargs):
        media = self.get_object()

        try:
            # Delete files on S3
            delete_object(media.organization.bucket_name, '{}/thumb.jpg'.format(media.video_id),
                          media.organization.aws_account)

            media.has_thumbnail = False
            media.save()

        except Exception as e:
            return Response(data=str(e), status=HTTP_400_BAD_REQUEST)

        return Response(status=HTTP_200_OK)
