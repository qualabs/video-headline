from rest_framework import viewsets

from api.serializers import OrganizationSerializer
from organization.models import Organization


class OrganizationViewSet(viewsets.ModelViewSet):
    serializer_class = OrganizationSerializer

    def get_queryset(self):
        user = self.request.user

        return Organization.objects.filter(id=user.organization_id)
