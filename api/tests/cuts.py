import logging
from unittest import mock

from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase
from datetime import timedelta
from django_fsm import TransitionNotAllowed

from api.serializers.cuts import LiveVideoCutSerializer
from test_utils import create_organizations, create_user, create_superuser, create_live_videos, \
    create_live_cut, create_key
from video.models import LiveVideoCut, LiveVideo


class LiveVideoCutTests(APITestCase):

    @classmethod
    def setUpClass(cls):
        logging.disable(logging.WARNING)

        # Organizations
        cls.org1, cls.org2 = create_organizations('Organization', 2)

        # Users and Superuser
        cls.user1 = create_user('user1', '12345678', cls.org1)
        cls.user2 = create_user('user2', '12345678', cls.org2)
        cls.su = create_superuser('admin', '12345678', cls.org1)
        cls.key = create_key('key', cls.user1)

    def setUp(self):
        # Videos
        self.live1 = create_live_videos('Video', self.user1, self.org1, 1)[0]
        self.live2 = create_live_videos('Video', self.user2, self.org2, 1)[0]

        # Cuts
        self.cut1 = create_live_cut(self.live1, timezone.now() + timedelta(days=1),
                                    timezone.now() + timedelta(days=1, hours=2))
        self.cut2 = create_live_cut(self.live1, timezone.now() + timedelta(days=1, hours=4),
                                    timezone.now() + timedelta(days=1, hours=6))
        self.cut3 = create_live_cut(self.live2, timezone.now() + timedelta(days=1, hours=1),
                                    timezone.now() + timedelta(days=1, hours=3))
        self.cut4 = create_live_cut(self.live2, timezone.now() + timedelta(days=1, hours=5),
                                    timezone.now() + timedelta(days=1, hours=7))

    def tearDown(self):
        cuts = LiveVideoCut.objects.all()
        cuts._raw_delete(cuts.db)

    @classmethod
    def tearDownClass(cls):
        logging.disable(logging.NOTSET)
        cls.org1.delete()
        cls.org2.delete()

    # <editor-fold desc="List Cuts TESTS">
    def test_list_cuts_with_annon_user(self):
        url = reverse('cuts-list')
        response = self.client.get(url, format='json')

        # Validate status code
        self.assertEqual(status.HTTP_401_UNAUTHORIZED, response.status_code)

    def test_list_cuts_with_superuser(self):
        cut1 = LiveVideoCutSerializer(self.cut1).data
        cut2 = LiveVideoCutSerializer(self.cut2).data
        cut3 = LiveVideoCutSerializer(self.cut3).data
        cut4 = LiveVideoCutSerializer(self.cut4).data

        self.client.login(username='admin', password='12345678')

        url = reverse('cuts-list')
        response = self.client.get(url, format='json')

        # Validate status code
        self.assertEqual(status.HTTP_200_OK, response.status_code)

        # Validate cuts in results
        self.assertIn(cut1, response.json()['results'])
        self.assertIn(cut2, response.json()['results'])
        self.assertNotIn(cut3, response.json()['results'])
        self.assertNotIn(cut4, response.json()['results'])

    def test_list_cuts_with_user_1(self):
        cut1 = LiveVideoCutSerializer(self.cut1).data
        cut2 = LiveVideoCutSerializer(self.cut2).data
        cut3 = LiveVideoCutSerializer(self.cut3).data
        cut4 = LiveVideoCutSerializer(self.cut4).data

        self.client.login(username='user1', password='12345678')

        url = reverse('cuts-list')
        response = self.client.get(url, format='json')

        # Validate status code
        self.assertEqual(status.HTTP_200_OK, response.status_code)

        # Validate cuts in results
        self.assertIn(cut1, response.json()['results'])
        self.assertIn(cut2, response.json()['results'])
        self.assertNotIn(cut3, response.json()['results'])
        self.assertNotIn(cut4, response.json()['results'])

    def test_list_cuts_with_user_2(self):
        cut1 = LiveVideoCutSerializer(self.cut1).data
        cut2 = LiveVideoCutSerializer(self.cut2).data
        cut3 = LiveVideoCutSerializer(self.cut3).data
        cut4 = LiveVideoCutSerializer(self.cut4).data

        self.client.login(username='user2', password='12345678')

        url = reverse('cuts-list')
        response = self.client.get(url, format='json')

        # Validate status code
        self.assertEqual(status.HTTP_200_OK, response.status_code)

        # Validate cuts in results
        self.assertNotIn(cut1, response.json()['results'])
        self.assertNotIn(cut2, response.json()['results'])
        self.assertIn(cut3, response.json()['results'])
        self.assertIn(cut4, response.json()['results'])

    def test_list_cuts_with_key(self):
        cut1 = LiveVideoCutSerializer(self.cut1).data
        cut2 = LiveVideoCutSerializer(self.cut2).data
        cut3 = LiveVideoCutSerializer(self.cut3).data
        cut4 = LiveVideoCutSerializer(self.cut4).data

        url = reverse('cuts-list')
        header = {'HTTP_AUTHORIZATION': self.key.api_key}
        response = self.client.get(url, format='json', **header)

        # Validate status code
        self.assertEqual(status.HTTP_200_OK, response.status_code)

        # Validate cuts in results
        self.assertIn(cut1, response.json()['results'])
        self.assertIn(cut2, response.json()['results'])
        self.assertNotIn(cut3, response.json()['results'])
        self.assertNotIn(cut4, response.json()['results'])

    # </editor-fold>

    # <editor-fold desc="Retrieve Cuts TESTS">
    def test_retrieve_cut_with_annon_user(self):
        url = reverse('cuts-detail', kwargs={'pk': self.cut1.pk})
        response = self.client.get(url, content_type='application/json')

        # Validate status code
        self.assertEqual(status.HTTP_401_UNAUTHORIZED, response.status_code)

    def test_retrieve_cut_with_superuser(self):
        cut1 = LiveVideoCutSerializer(self.cut1).data
        self.client.login(username='admin', password='12345678')

        url = reverse('cuts-detail', kwargs={'pk': self.cut1.pk})
        response = self.client.get(url, content_type='application/json')

        # Validate status code
        self.assertEqual(status.HTTP_200_OK, response.status_code)

        # Validate cut
        self.assertEqual(cut1, response.data)

    def test_retrieve_cut_with_user_1(self):
        cut2 = LiveVideoCutSerializer(self.cut2).data
        self.client.login(username='user1', password='12345678')

        url = reverse('cuts-detail', kwargs={'pk': self.cut2.pk})
        response = self.client.get(url, content_type='application/json')

        # Validate status code
        self.assertEqual(status.HTTP_200_OK, response.status_code)

        # Validate cut
        self.assertEqual(cut2, response.data)

    def test_retrieve_cut_with_user_2(self):
        cut3 = LiveVideoCutSerializer(self.cut3).data
        self.client.login(username='user2', password='12345678')

        url = reverse('cuts-detail', kwargs={'pk': self.cut3.pk})
        response = self.client.get(url, content_type='application/json')

        # Validate status code
        self.assertEqual(status.HTTP_200_OK, response.status_code)

        # Validate cut
        self.assertEqual(cut3, response.data)

    def test_retrieve_cut_with_user_from_different_org(self):
        self.client.login(username='admin', password='12345678')

        url = reverse('cuts-detail', kwargs={'pk': self.cut4.pk})
        response = self.client.get(url, content_type='application/json')

        # Validate status code
        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)

    def test_retrieve_cut_with_key(self):
        cut2 = LiveVideoCutSerializer(self.cut2).data
        url1 = reverse('cuts-detail', kwargs={'pk': self.cut2.pk})
        url2 = reverse('cuts-detail', kwargs={'pk': self.cut4.pk})

        header = {'HTTP_AUTHORIZATION': self.key.api_key}
        response1 = self.client.get(url1, content_type='application/json', **header)
        response2 = self.client.get(url2, content_type='application/json', **header)

        # Validate status code
        self.assertEqual(status.HTTP_200_OK, response1.status_code)
        self.assertEqual(status.HTTP_404_NOT_FOUND, response2.status_code)

        # Validate cut
        self.assertEqual(cut2, response1.data)

    # </editor-fold>

    # <editor-fold desc="Create Cuts TESTS">
    def test_create_cut_with_annon_user(self):
        data = {
            "live": self.live1.pk,
            "initial_time": timezone.now() + timedelta(days=2),
            "final_time": timezone.now() + timedelta(days=2, hours=2),
            "description": "Motivo"
        }

        url = reverse('cuts-list')
        response = self.client.post(url, data=data, format='json')

        # Validate status code
        self.assertEqual(status.HTTP_401_UNAUTHORIZED, response.status_code)

    def test_create_cut_with_superuser(self):
        data = {
            "live": self.live1.pk,
            "initial_time": timezone.now() + timedelta(days=2),
            "final_time": timezone.now() + timedelta(days=2, hours=2),
            "description": "Motivo"
        }

        self.client.login(username='admin', password='12345678')

        url = reverse('cuts-list')
        response = self.client.post(url, data=data, format='json')

        # Validate status code
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)

    def test_create_cut_with_user_1(self):
        data = {
            "live": self.live1.pk,
            "initial_time": timezone.now() + timedelta(days=2),
            "final_time": timezone.now() + timedelta(days=2, hours=2),
            "description": "Motivo"
        }

        self.client.login(username='user1', password='12345678')

        url = reverse('cuts-list')
        response = self.client.post(url, data=data, format='json')

        # Validate status code
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)

    def test_create_cut_with_user_from_different_org(self):
        data = {
            "live": self.live1.pk,
            "initial_time": timezone.now() + timedelta(days=2),
            "final_time": timezone.now() + timedelta(days=2, hours=2),
            "description": "Motivo"
        }

        self.client.login(username='user2', password='12345678')

        url = reverse('cuts-list')
        response = self.client.post(url, data=data, format='json')

        # Validate status code
        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)

    def test_create_cut_with_key(self):
        data1 = {
            "live": self.live1.pk,
            "initial_time": timezone.now() + timedelta(days=2),
            "final_time": timezone.now() + timedelta(days=2, hours=2),
            "description": "Motivo"
        }

        data2 = {
            "live": self.live2.pk,
            "initial_time": timezone.now() + timedelta(days=2),
            "final_time": timezone.now() + timedelta(days=2, hours=2),
            "description": "Motivo"
        }

        url = reverse('cuts-list')
        header = {'HTTP_AUTHORIZATION': self.key.api_key}
        response1 = self.client.post(url, data=data1, format='json', **header)
        response2 = self.client.post(url, data=data2, format='json', **header)

        # Validate status code
        self.assertEqual(status.HTTP_201_CREATED, response1.status_code)
        self.assertEqual(status.HTTP_403_FORBIDDEN, response2.status_code)

    def test_create_cut_with_same_initial_and_final_time(self):
        data = {
            "live": self.live1.pk,
            "initial_time": timezone.now() + timedelta(days=2),
            "final_time": timezone.now() + timedelta(days=2),
            "description": "Motivo"
        }

        self.client.login(username='admin', password='12345678')

        url = reverse('cuts-list')
        response = self.client.post(url, data=data, format='json')

        # Validate status code
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)

    def test_create_cut_without_initial_and_final_time(self):
        data = {
            "live": self.live2.pk,
            "initial_time": "",
            "final_time": "",
            "description": "Motivo"
        }

        self.client.login(username='user2', password='12345678')

        url = reverse('cuts-list')
        response = self.client.post(url, data=data, format='json')

        # Validate status code
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)

    def test_create_cut_with_initial_and_final_time_before_now(self):
        data = {
            "live": self.live1.pk,
            "initial_time": timezone.now() + timedelta(days=-2),
            "final_time": timezone.now() + timedelta(days=-1),
            "description": "Motivo"
        }

        self.client.login(username='user1', password='12345678')

        url = reverse('cuts-list')
        response = self.client.post(url, data=data, format='json')

        # Validate status code
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)

    def test_create_cut_with_initial_time_before_now(self):
        data = {
            "live": self.live1.pk,
            "initial_time": timezone.now() + timedelta(days=-2),
            "final_time": timezone.now() + timedelta(days=2),
            "description": "Motivo"
        }

        self.client.login(username='admin', password='12345678')

        url = reverse('cuts-list')
        response = self.client.post(url, data=data, format='json')

        # Validate status code
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)

    def test_create_cut_with_final_time_before_initial_time(self):
        data = {
            "live": self.live2.pk,
            "initial_time": timezone.now() + timedelta(days=4),
            "final_time": timezone.now() + timedelta(days=2),
            "description": "Motivo"
        }

        self.client.login(username='user2', password='12345678')

        url = reverse('cuts-list')
        response = self.client.post(url, data=data, format='json')

        # Validate status code
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)

    def test_create_cut_within_cut_1(self):
        data = {
            "live": self.live1.pk,
            "initial_time": timezone.now() + timedelta(days=1, minutes=30),
            "final_time": timezone.now() + timedelta(days=1, hours=1, minutes=30),
            "description": "Motivo"
        }

        self.client.login(username='admin', password='12345678')

        url = reverse('cuts-list')
        response = self.client.post(url, data=data, format='json')

        # Validate status code
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)

    def test_create_cut_including_cut_1(self):
        data = {
            "live": self.live1.pk,
            "initial_time": timezone.now() + timedelta(days=1, hours=-1),
            "final_time": timezone.now() + timedelta(days=1, hours=3),
            "description": "Motivo"
        }

        self.client.login(username='admin', password='12345678')

        url = reverse('cuts-list')
        response = self.client.post(url, data=data, format='json')

        # Validate status code
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)

    def test_create_cut_overlap_cut_1(self):
        data1 = {
            "live": self.live1.pk,
            "initial_time": timezone.now() + timedelta(days=1, hours=-1),
            "final_time": timezone.now() + timedelta(days=1, hours=1),
            "description": "Motivo"
        }

        data2 = {
            "live": self.live1.pk,
            "initial_time": timezone.now() + timedelta(days=1, hours=1, minutes=30),
            "final_time": timezone.now() + timedelta(days=1, hours=3),
            "description": "Motivo"
        }

        self.client.login(username='admin', password='12345678')

        url = reverse('cuts-list')
        response1 = self.client.post(url, data=data1, format='json')
        response2 = self.client.post(url, data=data2, format='json')

        # Validate status code
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response1.status_code)
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response2.status_code)

    # </editor-fold>

    # <editor-fold desc="Put Cuts TESTS">
    def test_put_cut_with_annon_user(self):
        data = {
            "live": self.live1.pk,
            "initial_time": timezone.now() + timedelta(days=2),
            "final_time": timezone.now() + timedelta(days=2, hours=2),
            "description": "Motivo"
        }

        url = reverse('cuts-detail', kwargs={'pk': self.cut1.pk})
        response = self.client.put(url, data=data, format='json')

        # Validate status code
        self.assertEqual(status.HTTP_401_UNAUTHORIZED, response.status_code)

    def test_put_cut_with_superuser(self):
        data = {
            "live": self.live1.pk,
            "initial_time": timezone.now() + timedelta(days=2),
            "final_time": timezone.now() + timedelta(days=2, hours=2),
            "description": "Motivo"
        }

        self.client.login(username='admin', password='12345678')

        url = reverse('cuts-detail', kwargs={'pk': self.cut1.pk})
        response = self.client.put(url, data=data, format='json')

        # Validate status code
        self.assertEqual(status.HTTP_200_OK, response.status_code)

        # Validate live id
        self.assertEqual(data['live'], response.json()['live'])

        # Validate initial time
        self.assertEqual(data['initial_time'].strftime("%Y-%m-%d" + "T" + "%H:%M:00" + "Z"),
                         response.json()['initial_time'])

        # Validate final time
        self.assertEqual(data['final_time'].strftime("%Y-%m-%d" + "T" + "%H:%M:00" + "Z"),
                         response.json()['final_time'])

    def test_put_cut_with_user_1(self):
        data = {
            "live": self.live1.pk,
            "initial_time": timezone.now() + timedelta(days=2),
            "final_time": timezone.now() + timedelta(days=2, hours=2),
            "description": "Motivo"
        }

        self.client.login(username='user1', password='12345678')

        url = reverse('cuts-detail', kwargs={'pk': self.cut1.pk})
        response = self.client.put(url, data=data, format='json')

        # Validate status code
        self.assertEqual(status.HTTP_200_OK, response.status_code)

        # Validate live id
        self.assertEqual(data['live'], response.json()['live'])

        # Validate initial time
        self.assertEqual(data['initial_time'].strftime("%Y-%m-%d" + "T" + "%H:%M:00" + "Z"),
                         response.json()['initial_time'])

        # Validate final time
        self.assertEqual(data['final_time'].strftime("%Y-%m-%d" + "T" + "%H:%M:00" + "Z"),
                         response.json()['final_time'])

    def test_put_cut_with_user_2(self):
        data = {
            "live": self.live2.pk,
            "initial_time": timezone.now() + timedelta(days=2),
            "final_time": timezone.now() + timedelta(days=2, hours=2),
            "description": "Motivo"
        }

        self.client.login(username='user2', password='12345678')

        url = reverse('cuts-detail', kwargs={'pk': self.cut3.pk})
        response = self.client.put(url, data=data, format='json')

        # Validate status code
        self.assertEqual(status.HTTP_200_OK, response.status_code)

        # Validate live id
        self.assertEqual(data['live'], response.json()['live'])

        # Validate initial time
        self.assertEqual(data['initial_time'].strftime("%Y-%m-%d" + "T" + "%H:%M:00" + "Z"),
                         response.json()['initial_time'])

        # Validate final time
        self.assertEqual(data['final_time'].strftime("%Y-%m-%d" + "T" + "%H:%M:00" + "Z"),
                         response.json()['final_time'])

    def test_put_cut_with_user_from_different_org(self):
        data = {
            "live": self.live2.pk,
            "initial_time": timezone.now() + timedelta(days=2),
            "final_time": timezone.now() + timedelta(days=2, hours=2),
            "description": "Motivo"
        }

        self.client.login(username='admin', password='12345678')

        url = reverse('cuts-detail', kwargs={'pk': self.cut3.pk})
        response = self.client.put(url, data=data, format='json')

        # Validate status code
        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)

    def test_put_cut_with_key(self):
        data1 = {
            "live": self.live1.pk,
            "initial_time": timezone.now() + timedelta(days=2),
            "final_time": timezone.now() + timedelta(days=2, hours=2),
            "description": "Motivo"
        }

        data2 = {
            "live": self.live2.pk,
            "initial_time": timezone.now() + timedelta(days=2),
            "final_time": timezone.now() + timedelta(days=2, hours=2),
            "description": "Motivo"
        }

        url1 = reverse('cuts-detail', kwargs={'pk': self.cut1.pk})
        url2 = reverse('cuts-detail', kwargs={'pk': self.cut3.pk})
        header = {'HTTP_AUTHORIZATION': self.key.api_key}
        response1 = self.client.put(url1, data=data1, format='json', **header)
        response2 = self.client.put(url2, data=data2, format='json', **header)

        # Validate status code
        self.assertEqual(status.HTTP_200_OK, response1.status_code)
        self.assertEqual(status.HTTP_404_NOT_FOUND, response2.status_code)

        # Validate live id
        self.assertEqual(data1['live'], response1.json()['live'])

        # Validate initial time
        self.assertEqual(data1['initial_time'].strftime("%Y-%m-%d" + "T" + "%H:%M:00" + "Z"),
                         response1.json()['initial_time'])

        # Validate final time
        self.assertEqual(data1['final_time'].strftime("%Y-%m-%d" + "T" + "%H:%M:00" + "Z"),
                         response1.json()['final_time'])

    def test_put_cut_with_same_initial_and_final_time(self):
        data = {
            "live": self.live1.pk,
            "initial_time": timezone.now() + timedelta(days=2),
            "final_time": timezone.now() + timedelta(days=2),
            "description": "Motivo"
        }

        self.client.login(username='admin', password='12345678')

        url = reverse('cuts-detail', kwargs={'pk': self.cut1.pk})
        response = self.client.put(url, data=data, format='json')

        # Validate status code
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)

    def test_put_cut_without_initial_and_final_time(self):
        data = {
            "live": self.live1.pk,
            "initial_time": "",
            "final_time": "",
            "description": "Motivo"
        }

        self.client.login(username='admin', password='12345678')

        url = reverse('cuts-detail', kwargs={'pk': self.cut1.pk})
        response = self.client.put(url, data=data, format='json')

        # Validate status code
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)

    def test_put_cut_with_initial_and_final_time_before_now(self):
        data = {
            "live": self.live1.pk,
            "initial_time": timezone.now() + timedelta(days=-2),
            "final_time": timezone.now() + timedelta(days=-1),
            "description": "Motivo"
        }

        self.client.login(username='admin', password='12345678')

        url = reverse('cuts-detail', kwargs={'pk': self.cut1.pk})
        response = self.client.put(url, data=data, format='json')

        # Validate status code
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)

    def test_put_cut_with_initial_time_before_now(self):
        data = {
            "live": self.live1.pk,
            "initial_time": timezone.now() + timedelta(days=-2),
            "final_time": timezone.now() + timedelta(days=2),
            "description": "Motivo"
        }

        self.client.login(username='admin', password='12345678')

        url = reverse('cuts-detail', kwargs={'pk': self.cut1.pk})
        response = self.client.put(url, data=data, format='json')

        # Validate status code
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)

    def test_put_cut_with_final_time_before_initial_time(self):
        data = {
            "live": self.live1.pk,
            "initial_time": timezone.now() + timedelta(days=4),
            "final_time": timezone.now() + timedelta(days=2),
            "description": "Motivo"
        }

        self.client.login(username='admin', password='12345678')

        url = reverse('cuts-detail', kwargs={'pk': self.cut1.pk})
        response = self.client.put(url, data=data, format='json')

        # Validate status code
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)

    def test_put_cut_within_cut_1(self):
        data = {
            "live": self.live1.pk,
            "initial_time": timezone.now() + timedelta(days=1, minutes=30),
            "final_time": timezone.now() + timedelta(days=1, hours=1, minutes=30),
            "description": "Motivo"
        }

        self.client.login(username='admin', password='12345678')

        url = reverse('cuts-detail', kwargs={'pk': self.cut2.pk})
        response = self.client.put(url, data=data, format='json')

        # Validate status code
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)

    def test_put_cut_including_cut_1(self):
        data = {
            "live": self.live1.pk,
            "initial_time": timezone.now() + timedelta(days=1, hours=-1),
            "final_time": timezone.now() + timedelta(days=1, hours=3),
            "description": "Motivo"
        }

        self.client.login(username='admin', password='12345678')

        url = reverse('cuts-detail', kwargs={'pk': self.cut2.pk})
        response = self.client.put(url, data=data, format='json')

        # Validate status code
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)

    def test_put_cut_overlap_cut_1(self):
        data1 = {
            "live": self.live1.pk,
            "initial_time": timezone.now() + timedelta(days=1, hours=-1),
            "final_time": timezone.now() + timedelta(days=1, hours=1),
            "description": "Motivo"
        }

        data2 = {
            "live": self.live1.pk,
            "initial_time": timezone.now() + timedelta(days=1, hours=1, minutes=30),
            "final_time": timezone.now() + timedelta(days=1, hours=3)
        }

        self.client.login(username='admin', password='12345678')

        url = reverse('cuts-detail', kwargs={'pk': self.cut2.pk})
        response1 = self.client.put(url, data=data1, format='json')
        response2 = self.client.put(url, data=data2, format='json')

        # Validate status code
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response1.status_code)
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response2.status_code)

    # </editor-fold>

    # <editor-fold desc="Patch Cuts TESTS">
    def test_patch_cut_with_annon_user(self):
        url = reverse('cuts-detail', kwargs={'pk': self.cut1.pk})
        response = self.client.patch(url, content_type='application/json')

        # Validate status code
        self.assertEqual(status.HTTP_401_UNAUTHORIZED, response.status_code)

    def test_patch_cut_with_superuser(self):
        data = {
            "final_time": timezone.now() + timedelta(days=1, hours=3)
        }

        self.client.login(username='admin', password='12345678')

        url = reverse('cuts-detail', kwargs={'pk': self.cut1.pk})
        response = self.client.patch(url, data=data, format='json')

        # Validate status code
        self.assertEqual(status.HTTP_200_OK, response.status_code)

        # Validate live id
        self.assertEqual(self.live1.pk, response.json()['live'])

        # Validate initial time
        self.assertEqual(self.cut1.initial_time.strftime("%Y-%m-%d" + "T" + "%H:%M:%S" + "Z"),
                         response.json()['initial_time'])

        # Validate final time
        self.assertEqual(data['final_time'].strftime("%Y-%m-%d" + "T" + "%H:%M:00" + "Z"),
                         response.json()['final_time'])

    def test_patch_cut_with_user_1(self):
        data = {
            "initial_time": timezone.now() + timedelta(days=1, hours=-1)
        }

        self.client.login(username='user1', password='12345678')

        url = reverse('cuts-detail', kwargs={'pk': self.cut1.pk})
        response = self.client.patch(url, data=data, format='json')

        # Validate status code
        self.assertEqual(status.HTTP_200_OK, response.status_code)

        # Validate live id
        self.assertEqual(self.live1.pk, response.json()['live'])

        # Validate initial time
        self.assertEqual(data['initial_time'].strftime(
            "%Y-%m-%d" + "T" + "%H:%M:00" + "Z"), response.json()['initial_time'])

        # Validate final time
        self.assertEqual(self.cut1.final_time.strftime(
            "%Y-%m-%d" + "T" + "%H:%M:%S" + "Z"), response.json()['final_time'])

    def test_patch_cut_with_user_from_different_org(self):
        data = {
            "final_time": timezone.now() + timedelta(days=2, hours=2)
        }

        self.client.login(username='user2', password='12345678')

        url = reverse('cuts-detail', kwargs={'pk': self.cut1.pk})
        response = self.client.patch(url, data=data, format='json')

        # Validate status code
        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)

    def test_patch_cut_with_key(self):
        data = {
            "initial_time": timezone.now() + timedelta(days=1, hours=-1)
        }

        url1 = reverse('cuts-detail', kwargs={'pk': self.cut1.pk})
        url2 = reverse('cuts-detail', kwargs={'pk': self.cut3.pk})
        header = {'HTTP_AUTHORIZATION': self.key.api_key}
        response1 = self.client.patch(url1, data=data, format='json', **header)
        response2 = self.client.put(url2, data=data, format='json', **header)

        # Validate status code
        self.assertEqual(status.HTTP_200_OK, response1.status_code)
        self.assertEqual(status.HTTP_404_NOT_FOUND, response2.status_code)

        # Validate live id
        self.assertEqual(self.live1.pk, response1.json()['live'])

        # Validate initial time
        self.assertEqual(data['initial_time'].strftime(
            "%Y-%m-%d" + "T" + "%H:%M:00" + "Z"), response1.json()['initial_time'])

        # Validate final time
        self.assertEqual(self.cut1.final_time.strftime(
            "%Y-%m-%d" + "T" + "%H:%M:%S" + "Z"), response1.json()['final_time'])

    def test_patch_cut_with_same_initial_and_final_time(self):
        data = {
            "live": self.live1.pk,
            "initial_time": timezone.now() + timedelta(days=2),
            "final_time": timezone.now() + timedelta(days=2)
        }

        self.client.login(username='admin', password='12345678')

        url = reverse('cuts-detail', kwargs={'pk': self.cut1.pk})
        response = self.client.patch(url, data=data, format='json')

        # Validate status code
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)

    def test_patch_cut_without_initial_and_final_time(self):
        data = {
            "live": self.live1.pk,
            "initial_time": "",
            "final_time": ""
        }

        self.client.login(username='admin', password='12345678')

        url = reverse('cuts-detail', kwargs={'pk': self.cut1.pk})
        response = self.client.patch(url, data=data, format='json')

        # Validate status code
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)

    def test_patch_cut_with_initial_and_final_time_before_now(self):
        data = {
            "live": self.live1.pk,
            "initial_time": timezone.now() + timedelta(days=-2),
            "final_time": timezone.now() + timedelta(days=-1)
        }

        self.client.login(username='admin', password='12345678')

        url = reverse('cuts-detail', kwargs={'pk': self.cut1.pk})
        response = self.client.patch(url, data=data, format='json')

        # Validate status code
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)

    def test_patch_cut_with_initial_time_before_now(self):
        data = {
            "live": self.live1.pk,
            "initial_time": timezone.now() + timedelta(days=-2),
            "final_time": timezone.now() + timedelta(days=2)
        }

        self.client.login(username='admin', password='12345678')

        url = reverse('cuts-detail', kwargs={'pk': self.cut1.pk})
        response = self.client.patch(url, data=data, format='json')

        # Validate status code
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)

    def test_patch_cut_with_final_time_before_initial_time(self):
        data = {
            "live": self.live1.pk,
            "initial_time": timezone.now() + timedelta(days=4),
            "final_time": timezone.now() + timedelta(days=2)
        }

        self.client.login(username='admin', password='12345678')

        url = reverse('cuts-detail', kwargs={'pk': self.cut1.pk})
        response = self.client.patch(url, data=data, format='json')

        # Validate status code
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)

    def test_patch_cut_within_cut_1(self):
        data = {
            "live": self.live1.pk,
            "initial_time": timezone.now() + timedelta(days=1, minutes=30),
            "final_time": timezone.now() + timedelta(days=1, hours=1, minutes=30)
        }

        self.client.login(username='admin', password='12345678')

        url = reverse('cuts-detail', kwargs={'pk': self.cut2.pk})
        response = self.client.patch(url, data=data, format='json')

        # Validate status code
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)

    def test_patch_cut_including_cut_1(self):
        data = {
            "live": self.live1.pk,
            "initial_time": timezone.now() + timedelta(days=1, hours=-1),
            "final_time": timezone.now() + timedelta(days=1, hours=3)
        }

        self.client.login(username='admin', password='12345678')

        url = reverse('cuts-detail', kwargs={'pk': self.cut2.pk})
        response = self.client.patch(url, data=data, format='json')

        # Validate status code
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)

    def test_patch_cut_overlap_cut_1(self):
        data1 = {
            "live": self.live1.pk,
            "initial_time": timezone.now() + timedelta(days=1, hours=-1),
            "final_time": timezone.now() + timedelta(days=1, hours=1)
        }

        data2 = {
            "live": self.live1.pk,
            "initial_time": timezone.now() + timedelta(days=1, hours=1, minutes=30),
            "final_time": timezone.now() + timedelta(days=1, hours=3)
        }

        self.client.login(username='admin', password='12345678')

        url = reverse('cuts-detail', kwargs={'pk': self.cut2.pk})
        response1 = self.client.patch(url, data=data1, format='json')
        response2 = self.client.patch(url, data=data2, format='json')

        # Validate status code
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response1.status_code)
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response2.status_code)

    # </editor-fold>

    # <editor-fold desc="Delete Cuts TESTS">
    def test_delete_cut_with_annon_user(self):
        url = reverse('cuts-detail', kwargs={'pk': self.cut1.pk})
        response = self.client.delete(url, content_type='application/json')

        # Validate status code
        self.assertEqual(status.HTTP_401_UNAUTHORIZED, response.status_code)

    def test_delete_cut_with_superuser(self):
        self.client.login(username='admin', password='12345678')

        url = reverse('cuts-detail', kwargs={'pk': self.cut1.pk})
        response = self.client.delete(url, content_type='application/json')

        # Validate status code
        self.assertEqual(status.HTTP_204_NO_CONTENT, response.status_code)

    def test_delete_cut_with_user_1(self):
        self.client.login(username='user1', password='12345678')

        url = reverse('cuts-detail', kwargs={'pk': self.cut1.pk})
        response = self.client.delete(url, content_type='application/json')
        # Validate status code
        self.assertEqual(status.HTTP_204_NO_CONTENT, response.status_code)

    def test_delete_cut_with_user_from_different_org(self):
        self.client.login(username='user2', password='12345678')

        url = reverse('cuts-detail', kwargs={'pk': self.cut1.pk})
        response = self.client.delete(url, content_type='application/json')

        # Validate status code
        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)

    def test_delete_cut_with_key(self):
        url1 = reverse('cuts-detail', kwargs={'pk': self.cut1.pk})
        url2 = reverse('cuts-detail', kwargs={'pk': self.cut3.pk})
        header = {'HTTP_AUTHORIZATION': self.key.api_key}
        response1 = self.client.delete(url1, content_type='application/json', **header)
        response2 = self.client.delete(url2, content_type='application/json', **header)

        # Validate status code
        self.assertEqual(status.HTTP_204_NO_CONTENT, response1.status_code)
        self.assertEqual(status.HTTP_404_NOT_FOUND, response2.status_code)

    def test_delete_cut_with_status_schedule(self):
        live = LiveVideo.objects.create(
            name='Video 1',
            created_by=self.su,
            organization=self.org1,
            state=LiveVideo.State.ON
        )

        cut = LiveVideoCut.objects.create(
            live=live,
            initial_time=timezone.now() + timedelta(days=3),
            final_time=timezone.now() + timedelta(days=3, hours=2),
            state=LiveVideoCut.State.SCHEDULED
        )

        self.client.login(username='admin', password='12345678')

        url = reverse('cuts-detail', kwargs={'pk': cut.pk})
        response = self.client.delete(url, content_type='application/json')

        self.assertEqual(status.HTTP_204_NO_CONTENT, response.status_code)

    def test_delete_cut_with_status_executing(self):
        live = LiveVideo.objects.create(
            name='Video 1',
            created_by=self.su,
            organization=self.org1,
            state=LiveVideo.State.OFF
        )

        cut = LiveVideoCut.objects.create(
            live=live,
            initial_time=timezone.now() + timedelta(days=3),
            final_time=timezone.now() + timedelta(days=3, hours=2),
            state=LiveVideoCut.State.EXECUTING
        )

        self.client.login(username='admin', password='12345678')

        url = reverse('cuts-detail', kwargs={'pk': cut.pk})

        response = self.client.delete(url, content_type='application/json')
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)

    def test_delete_cut_with_status_performed(self):
        live = LiveVideo.objects.create(
            name='Video 1',
            created_by=self.su,
            organization=self.org1,
            state=LiveVideo.State.ON
        )

        cut = LiveVideoCut.objects.create(
            live=live,
            initial_time=timezone.now() + timedelta(days=3),
            final_time=timezone.now() + timedelta(days=3, hours=2),
            state=LiveVideoCut.State.PERFORMED
        )

        self.client.login(username='admin', password='12345678')

        url = reverse('cuts-detail', kwargs={'pk': cut.pk})

        response = self.client.delete(url, content_type='application/json')
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)

    # </editor-fold>

    # <editor-fold desc="Transition by model LiveVideoCut TESTS">
    def test_change_cut_status_from_scheduled_to_executing(self):
        live = LiveVideo.objects.create(
            name='Video 1',
            created_by=self.user1,
            organization=self.org1,
            state=LiveVideo.State.ON
        )

        cut = LiveVideoCut.objects.create(
            live=live,
            initial_time=timezone.now() + timedelta(days=3),
            final_time=timezone.now() + timedelta(days=3, hours=2),
            description='Motivo',
            state=LiveVideoCut.State.SCHEDULED
        )

        self.client.login(username='user1', password='12345678')

        with mock.patch('utils.medialive.stop_channel', side_effect=None):
            cut.to_executing()

        live_updated = LiveVideo.objects.get(id=live.pk)
        cut_updated = LiveVideoCut.objects.get(id=cut.pk)

        # Validate live and cut state
        self.assertEqual(LiveVideo.State.STOPPING, live_updated.state)
        self.assertEqual(LiveVideoCut.State.EXECUTING, cut_updated.state)

    def test_change_cut_status_from_executing_to_performed(self):
        live = LiveVideo.objects.create(
            name='Video 1',
            created_by=self.user1,
            organization=self.org1,
            state=LiveVideo.State.OFF
        )

        cut = LiveVideoCut.objects.create(
            live=live,
            initial_time=timezone.now() + timedelta(days=3),
            final_time=timezone.now() + timedelta(days=3, hours=2),
            description='Motivo',
            state=LiveVideoCut.State.EXECUTING
        )

        self.client.login(username='user1', password='12345678')

        with mock.patch('utils.medialive.start_channel', side_effect=None):
            cut.to_performed()

        live_updated = LiveVideo.objects.get(id=live.pk)
        cut_updated = LiveVideoCut.objects.get(id=cut.pk)

        # Validate live and cut state
        self.assertEqual(LiveVideo.State.STARTING, live_updated.state)
        self.assertEqual(LiveVideoCut.State.PERFORMED, cut_updated.state)

    def test_change_cut_status_from_executing_to_executing(self):
        live = LiveVideo.objects.create(
            name='Video 1',
            created_by=self.user1,
            organization=self.org1,
            state=LiveVideo.State.OFF
        )

        cut = LiveVideoCut.objects.create(
            live=live,
            initial_time=timezone.now() + timedelta(days=3),
            final_time=timezone.now() + timedelta(days=3, hours=2),
            description='Motivo',
            state=LiveVideoCut.State.EXECUTING
        )

        self.client.login(username='user1', password='12345678')

        with self.assertRaises(TransitionNotAllowed):
            cut.to_executing()

    def test_change_cut_status_from_performed_to_performed(self):
        live = LiveVideo.objects.create(
            name='Video 1',
            created_by=self.user1,
            organization=self.org1,
            state=LiveVideo.State.ON
        )

        cut = LiveVideoCut.objects.create(
            live=live,
            initial_time=timezone.now() + timedelta(days=3),
            final_time=timezone.now() + timedelta(days=3, hours=2),
            description='Motivo',
            state=LiveVideoCut.State.PERFORMED
        )

        self.client.login(username='user1', password='12345678')

        with self.assertRaises(TransitionNotAllowed):
            cut.to_performed()

    def test_change_cut_status_from_scheduled_to_performed(self):
        live = LiveVideo.objects.create(
            name='Video 1',
            created_by=self.user1,
            organization=self.org1,
            state=LiveVideo.State.ON
        )

        cut = LiveVideoCut.objects.create(
            live=live,
            initial_time=timezone.now() + timedelta(days=3),
            final_time=timezone.now() + timedelta(days=3, hours=2),
            description='Motivo',
            state=LiveVideoCut.State.SCHEDULED
        )

        self.client.login(username='user1', password='12345678')

        with self.assertRaises(TransitionNotAllowed):
            cut.to_performed()

    def test_change_cut_status_from_performed_to_executing(self):
        live = LiveVideo.objects.create(
            name='Video 1',
            created_by=self.user1,
            organization=self.org1,
            state=LiveVideo.State.ON
        )

        cut = LiveVideoCut.objects.create(
            live=live,
            initial_time=timezone.now() + timedelta(days=3),
            final_time=timezone.now() + timedelta(days=3, hours=2),
            description='Motivo',
            state=LiveVideoCut.State.PERFORMED
        )

        self.client.login(username='user1', password='12345678')

        with self.assertRaises(TransitionNotAllowed):
            cut.to_executing()

    # </editor-fold>
