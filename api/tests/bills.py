import logging
from datetime import date

from django.utils import timezone
from dateutil.relativedelta import relativedelta
from unittest import mock

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from api.serializers import MinBillSerializer, BillSerializer
from organization.models import Bill
from test_utils import (
    create_user,
    create_superuser,
    create_key,
    create_organizations,
    create_plans,
    create_bill,
)


class BillTests(APITestCase):
    @classmethod
    def setUpClass(cls):
        logging.disable(logging.WARNING)

        cls.org1, cls.org2 = create_organizations('Organization', 2)

        cls.user1 = create_user('user1', '12345678', cls.org1)
        cls.user2 = create_user('user2', '12345678', cls.org2)
        cls.su = create_superuser('admin', '12345678', cls.org1)
        cls.key = create_key('key', cls.user1)

        cls.plan1, cls.plan2 = create_plans('Plan', 2)

    def setUp(self):
        self.bill1 = create_bill(
            self.org1, self.plan1, date.today().replace(day=1)
        )
        self.bill2 = create_bill(
            self.org2, self.plan1, date.today().replace(day=1)
        )
        self.bill3 = create_bill(
            self.org1,
            self.plan1,
            date.today().replace(day=1) - relativedelta(months=1),
        )

    def tearDown(self):
        Bill.objects.all().delete()

    @classmethod
    def tearDownClass(cls):
        logging.disable(logging.NOTSET)
        cls.plan1.delete()
        cls.plan2.delete()
        cls.org1.delete()
        cls.org2.delete()

    # <editor-fold desc="List Bill TESTS">
    def test_list_bills_with_annon_user(self):
        url = reverse('bills-list')
        response = self.client.get(url, format='json')

        # Validate status code
        self.assertEqual(status.HTTP_401_UNAUTHORIZED, response.status_code)

    def test_list_bills_with_superuser(self):
        bill1 = MinBillSerializer(self.bill1).data
        bill2 = MinBillSerializer(self.bill2).data

        self.client.login(username='admin', password='12345678')

        url = reverse('bills-list')
        response = self.client.get(url, format='json')

        # Validate status code
        self.assertEqual(status.HTTP_200_OK, response.status_code)

        # Validate bills in results
        self.assertIn(bill1, response.json()['results'])
        self.assertNotIn(bill2, response.json()['results'])

    def test_list_bills_with_user2(self):
        bill1 = MinBillSerializer(self.bill1).data
        bill2 = MinBillSerializer(self.bill2).data

        self.client.login(username='user2', password='12345678')

        url = reverse('bills-list')
        response = self.client.get(url, format='json')

        # Validate status code
        self.assertEqual(status.HTTP_200_OK, response.status_code)

        # Validate channels in results
        self.assertNotIn(bill1, response.json()['results'])
        self.assertIn(bill2, response.json()['results'])

    def test_list_bills_with_key(self):
        bill1 = MinBillSerializer(self.bill1).data
        bill2 = MinBillSerializer(self.bill2).data

        url = reverse('bills-list')
        header = {'HTTP_AUTHORIZATION': self.key.api_key}
        response = self.client.get(url, format='json', **header)

        # Validate status code
        self.assertEqual(status.HTTP_200_OK, response.status_code)

        # Validate bills in results
        self.assertIn(bill1, response.json()['results'])
        self.assertNotIn(bill2, response.json()['results'])

    # </editor-fold>

    # <editor-fold desc="Retrieve Bill TESTS">
    def test_retrieve_bill_with_annon_user(self):
        url = reverse('bills-detail', kwargs={'pk': self.bill1.pk})
        response = self.client.get(url, format='json')

        # Validate status code
        self.assertEqual(status.HTTP_401_UNAUTHORIZED, response.status_code)

    def test_retrieve_bill_with_superuser(self):
        bill1 = BillSerializer(self.bill1).data
        self.client.login(username='admin', password='12345678')

        url = reverse('bills-detail', kwargs={'pk': self.bill1.pk})
        response = self.client.get(url, content_type='application/json')

        # Validate status code
        self.assertEqual(status.HTTP_200_OK, response.status_code)

        # Validate bill
        self.assertEqual(bill1, response.data)

    def test_retrieve_bill_with_user1(self):
        bill1 = BillSerializer(self.bill1).data
        self.client.login(username='user1', password='12345678')

        url = reverse('bills-detail', kwargs={'pk': self.bill1.pk})
        response = self.client.get(url, content_type='application/json')

        # Validate status code
        self.assertEqual(status.HTTP_200_OK, response.status_code)

        # Validate bill
        self.assertEqual(bill1, response.data)

    def test_retrieve_bill_with_user_from_different_org(self):
        self.client.login(username='user2', password='12345678')

        url = reverse('bills-detail', kwargs={'pk': self.bill1.pk})
        response = self.client.get(url, content_type='application/json')

        # Validate status code
        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)

    def test_retrieve_bill_with_key(self):
        bill1 = BillSerializer(self.bill1).data
        url1 = reverse('bills-detail', kwargs={'pk': self.bill1.pk})
        url2 = reverse('bills-detail', kwargs={'pk': self.bill2.pk})

        header = {'HTTP_AUTHORIZATION': self.key.api_key}
        response1 = self.client.get(url1, format='json', **header)
        response2 = self.client.get(url2, format='json', **header)

        # Validate status code
        self.assertEqual(status.HTTP_200_OK, response1.status_code)
        self.assertEqual(status.HTTP_404_NOT_FOUND, response2.status_code)

        # Validate bill
        self.assertEqual(bill1, response1.data)

    def test_retrieve_bill_with_invalid_id(self):
        self.client.login(username='user2', password='12345678')

        url = reverse('bills-detail', kwargs={'pk': '5'})
        response = self.client.get(url, content_type='application/json')

        # Validate status code
        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)

    def test_retrieve_bill_in_past_month(self):
        bill3 = BillSerializer(self.bill3).data
        self.client.login(username='user1', password='12345678')

        url = reverse('bills-detail', kwargs={'pk': self.bill3.pk})
        response = self.client.get(url, content_type='application/json')

        # Validate status code
        self.assertEqual(status.HTTP_200_OK, response.status_code)

        # Validate bill
        response = response.json()
        self.assertEqual(
            bill3['video_transcoding'], response['video_transcoding']
        )
        self.assertEqual(bill3['storage'], response['storage'])
        self.assertEqual(bill3['data_transfer'], response['data_transfer'])
        self.assertEqual(bill3['extras'], response['extras'])

    def test_retrieve_bill_in_current_month(self):
        update = timezone.now() - relativedelta(days=1)
        Bill.objects.filter(pk=self.bill1.pk).update(last_modified=update)

        bill1 = BillSerializer(self.bill1).data

        self.client.login(username='user1', password='12345678')
        url = reverse('bills-detail', kwargs={'pk': self.bill1.pk})

        with mock.patch('utils.costexplorer.update_bill', side_effect=None):
            response = self.client.get(url, content_type='application/json')

        # Validate status code
        self.assertEqual(status.HTTP_200_OK, response.status_code)

        # Validate bill
        response = response.json()
        self.assertEqual(
            bill1['video_transcoding'], response['video_transcoding']
        )
        self.assertEqual(bill1['storage'], response['storage'])
        self.assertEqual(bill1['data_transfer'], response['data_transfer'])
        self.assertEqual(bill1['extras'], response['extras'])

    # </editor-fold>
