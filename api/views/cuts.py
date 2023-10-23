from django.db import IntegrityError
from rest_framework import viewsets, status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from api.filters import LiveVideoCutsFilter
from api.serializers.cuts import LiveVideoCutSerializer, UpdateLiveVideoCutSerializer, \
    CreateLiveVideoCutSerializer
from video.models import LiveVideoCut


class LiveVideoCutsViewSet(viewsets.ModelViewSet):
    search_fields = (
        '=created_by__username',
        'description',
        '=live__video_id',
    )
    serializer_class = LiveVideoCutSerializer
    filterset_class = LiveVideoCutsFilter

    def get_queryset(self):
        user = self.request.user
        return LiveVideoCut.objects.filter(live__organization_id=user.organization_id).order_by(
            'initial_time')

    def get_serializer_class(self):
        serializer_class = {
            'create': CreateLiveVideoCutSerializer,
            'update': UpdateLiveVideoCutSerializer,
            'partial_update': UpdateLiveVideoCutSerializer,
        }

        if self.action and self.action in serializer_class.keys():
            return serializer_class[self.action]
        else:
            return self.serializer_class

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            cut = serializer.save(created_by=request.user)
        except IntegrityError as e:
            raise ValidationError(str(e))

        output = self.serializer_class(cut)
        return Response(output.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            cut = serializer.update(self.get_object(), serializer.validated_data)
        except IntegrityError as e:
            raise ValidationError(str(e))

        output = self.serializer_class(cut)
        return Response(output.data, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        cut = self.get_object()
        if cut.state in [LiveVideoCut.State.EXECUTING]:
            raise ValidationError(
                'You cannot delete a cut that is being executed.')
        if cut.state in [LiveVideoCut.State.PERFORMED]:
            raise ValidationError(
                'You cannot delete a cut that has already been executed.')

        return super(LiveVideoCutsViewSet, self).destroy(self, request, *args, **kwargs)
