from django.db import IntegrityError
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_201_CREATED

from api.serializers import (
    ChannelSerializer,
    CreateChannelSerializer,
    MediaSerializer,
)
from organization.models import Channel


class ChannelViewSet(viewsets.ModelViewSet):
    serializer_class = ChannelSerializer
    search_fields = ('name', 'organization__name')

    def get_queryset(self):
        user = self.request.user

        return Channel.objects.filter(
            organization_id=user.organization_id
        ).order_by('pk')

    def get_serializer_class(self):
        serializer_class = {
            'create': CreateChannelSerializer,
            'update': CreateChannelSerializer,
            'partial_update': CreateChannelSerializer,
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

        try:
            channel = Channel.objects.create(
                name=input_serializer.validated_data['name'],
                organization=organization,
                allowed_domains=input_serializer.validated_data.pop(
                    'allowed_domains', []
                ),
                ads_vast_url=input_serializer.validated_data.pop(
                    'ads_vast_url', ''
                ),
                autoplay=input_serializer.validated_data.pop(
                    'autoplay', False
                ),
            )

        except IntegrityError:
            raise ValidationError(
                {'non_field_errors': ['Error creating the channel']}
            )

        serialized = ChannelSerializer(channel)

        return Response(serialized.data, status=HTTP_201_CREATED)

    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated])
    def videos(self, request, pk, **kwargs):
        channel = self.get_object()
        data = channel.videos.all()
        page = self.paginate_queryset(data)

        serializer = MediaSerializer(
            page, many=True, context={'request': request}
        )
        paginated_serializer = self.get_paginated_response(serializer.data)

        return Response(paginated_serializer.data)
