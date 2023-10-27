from datetime import timedelta

from django.utils import timezone
from rest_framework import viewsets
from rest_framework.response import Response

from organization.models import Bill
from api.serializers import BillSerializer, MinBillSerializer
from utils import costexplorer


class BillsViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = BillSerializer
    search_fields = ('plan__name',)

    def get_queryset(self):
        user = self.request.user

        return Bill.objects.filter(
            organization_id=user.organization_id
        ).order_by('-date')

    def get_serializer_class(self):
        serializer_class = {
            'list': MinBillSerializer,
            'retrieve': BillSerializer,
        }

        if self.action and self.action in serializer_class.keys():
            return serializer_class[self.action]

    def retrieve(self, request, *args, **kwargs):
        bill = self.get_object()
        now = timezone.now()

        # If the current invoice is more than 12 hours out of date.
        if bill.is_current_bill() and (
            now > bill.last_modified + timedelta(hours=12)
        ):
            costexplorer.update_bill(bill)

        serializer = self.get_serializer(bill)

        return Response(serializer.data)
