from django.db import IntegrityError
from rest_framework import viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_405_METHOD_NOT_ALLOWED, HTTP_201_CREATED
from django.db.models import Count

from api.serializers.tag import TagSerializer, CreateTagSerializer
from video.models import Tag


class TagViewSet(viewsets.ModelViewSet):
    serializer_class = TagSerializer
    search_fields = (
        'name',
    )
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        queryset = Tag.objects.filter(organization_id=self.request.user.organization_id)
        if self.action and self.action in ['list']:
            queryset = queryset.annotate(Count('media')).order_by('-media__count')

        return queryset

    def get_serializer_class(self):
        serializer_class = {
            'create': CreateTagSerializer,
        }

        if self.action and self.action in serializer_class.keys():
            return serializer_class[self.action]

        else:
            return self.serializer_class

    # def list(self, request, *args, **kwargs):
    #     queryset = self.get_queryset().annotate(Count('videos')).order_by('-videos__count')

    #     serialized = self.get_serializer_class()(queryset, many=True)
    #     return Response(serialized.data)

    def create(self, request, *args, **kwargs):
        input_serializer = self.get_serializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)

        user = self.request.user
        organization = user.organization

        try:
            tag = Tag.objects.create(
                name=input_serializer.validated_data['name'],
                organization=organization,
            )

        except IntegrityError:
            raise ValidationError({'non_field_errors': ['Error creating tag.']})

        serialized = TagSerializer(tag)

        return Response(serialized.data, status=HTTP_201_CREATED)

    def partial_update(self, request, *args, **kwargs):
        return Response(status=HTTP_405_METHOD_NOT_ALLOWED)

    def update(self, request, *args, **kwargs):
        return Response(status=HTTP_405_METHOD_NOT_ALLOWED)
