import logging
import json
from unittest import mock
from urllib.parse import quote

from django.urls import reverse
from django_fsm import TransitionNotAllowed
from rest_framework import status
from rest_framework.test import APITestCase

from api.serializers.live_video import LiveVideoSerializer
from test_utils import (
    create_organizations,
    create_channels,
    create_live_videos,
    create_tags,
    create_live_video,
    create_user,
    create_superuser,
    add_channel_to_live_video,
    create_key,
)
from utils import medialive, sns
from video.models import LiveVideo


class LiveVideoTests(APITestCase):
    @classmethod
    def setUpClass(cls):
        logging.disable(logging.WARNING)

        cls.org1, cls.org2 = create_organizations('Organization', 2)

        cls.user1 = create_user('user1', '12345678', cls.org1)
        cls.user2 = create_user('user2', '12345678', cls.org2)
        cls.su = create_superuser('admin', '12345678', cls.org1)
        cls.key = create_key('key', cls.user1)

        cls.chan1, cls.chan2, cls.chan3 = create_channels(
            'Channel', cls.org1, 3
        )
        cls.chan4, cls.chan5 = create_channels('Channel', cls.org2, 2)

        cls.tag1, cls.tag2 = create_tags('Funny tag', cls.org1, 2)
        cls.tag3, cls.tag4 = create_tags('Funny tag', cls.org2, 2)

    def setUp(self):
        self.live1, self.live2, self.live3 = create_live_videos(
            'Video', self.user1, self.org1, 3
        )
        self.live4, self.live5 = create_live_videos(
            'Video', self.user2, self.org2, 2
        )

    def tearDown(self):
        LiveVideo.objects.all().delete()

    @classmethod
    def tearDownClass(cls):
        logging.disable(logging.NOTSET)
        cls.org1.delete()
        cls.org2.delete()

    # <editor-fold desc="List LiveVideo TESTS">
    def test_list_live_videos_with_annon_user(self):
        url = reverse('live-videos-list')
        response = self.client.get(url, format='json')

        # Validate status code
        self.assertEquals(status.HTTP_401_UNAUTHORIZED, response.status_code)

    def test_list_live_videos_with_superuser(self):
        live1 = LiveVideoSerializer(self.live1).data
        live2 = LiveVideoSerializer(self.live2).data
        live3 = LiveVideoSerializer(self.live3).data
        live4 = LiveVideoSerializer(self.live4).data
        live5 = LiveVideoSerializer(self.live5).data

        self.client.login(username='admin', password='12345678')

        url = reverse('live-videos-list')
        response = self.client.get(url, format='json')

        # Validate status code
        self.assertEqual(status.HTTP_200_OK, response.status_code)

        # Validate live_videos in results
        self.assertIn(live1, response.json()['results'])
        self.assertIn(live2, response.json()['results'])
        self.assertIn(live3, response.json()['results'])
        self.assertNotIn(live4, response.json()['results'])
        self.assertNotIn(live5, response.json()['results'])

    def test_list_live_videos_with_user_1(self):
        live1 = LiveVideoSerializer(self.live1).data
        live2 = LiveVideoSerializer(self.live2).data
        live3 = LiveVideoSerializer(self.live3).data
        live4 = LiveVideoSerializer(self.live4).data
        live5 = LiveVideoSerializer(self.live5).data

        self.client.login(username='user1', password='12345678')

        url = reverse('live-videos-list')
        response = self.client.get(url, format='json')

        # Validate status code
        self.assertEqual(status.HTTP_200_OK, response.status_code)

        # Validate live_videos in results
        self.assertIn(live1, response.json()['results'])
        self.assertIn(live2, response.json()['results'])
        self.assertIn(live3, response.json()['results'])
        self.assertNotIn(live4, response.json()['results'])
        self.assertNotIn(live5, response.json()['results'])

    def test_list_live_videos_with_user_2(self):
        live1 = LiveVideoSerializer(self.live1).data
        live2 = LiveVideoSerializer(self.live2).data
        live3 = LiveVideoSerializer(self.live3).data
        live4 = LiveVideoSerializer(self.live4).data
        live5 = LiveVideoSerializer(self.live5).data

        self.client.login(username='user2', password='12345678')

        url = reverse('live-videos-list')
        response = self.client.get(url, format='json')

        # Validate status code
        self.assertEqual(status.HTTP_200_OK, response.status_code)

        # Validate live_videos in results
        self.assertNotIn(live1, response.json()['results'])
        self.assertNotIn(live2, response.json()['results'])
        self.assertNotIn(live3, response.json()['results'])
        self.assertIn(live4, response.json()['results'])
        self.assertIn(live5, response.json()['results'])

    def test_list_live_videos_with_key(self):
        live1 = LiveVideoSerializer(self.live1).data
        live2 = LiveVideoSerializer(self.live2).data
        live3 = LiveVideoSerializer(self.live3).data
        live4 = LiveVideoSerializer(self.live4).data
        live5 = LiveVideoSerializer(self.live5).data

        url = reverse('live-videos-list')
        header = {'HTTP_AUTHORIZATION': self.key.api_key}
        response = self.client.get(url, format='json', **header)

        # Validate status code
        self.assertEqual(status.HTTP_200_OK, response.status_code)

        # Validate live_videos in results
        self.assertIn(live1, response.json()['results'])
        self.assertIn(live2, response.json()['results'])
        self.assertIn(live3, response.json()['results'])
        self.assertNotIn(live4, response.json()['results'])
        self.assertNotIn(live5, response.json()['results'])

    # </editor-fold>

    # <editor-fold desc="Retrieve LiveVideo TESTS">
    def test_retrieve_live_video_with_annon_user(self):
        url = reverse('live-videos-detail', kwargs={'pk': self.live1.pk})
        response = self.client.get(url, content_type='application/json')

        # Validate status code
        self.assertEqual(status.HTTP_401_UNAUTHORIZED, response.status_code)

    def test_retrieve_live_video_with_superuser_with_org_1(self):
        live1 = LiveVideoSerializer(self.live1).data
        self.client.login(username='admin', password='12345678')

        url = reverse('live-videos-detail', kwargs={'pk': self.live1.pk})
        response = self.client.get(url, content_type='application/json')

        # Validate status code
        self.assertEqual(status.HTTP_200_OK, response.status_code)

        # Validate live_video
        self.assertEqual(live1, response.data)

    def test_retrieve_live_video_with_user_from_different_org(self):
        self.client.login(username='admin', password='12345678')

        url = reverse('live-videos-detail', kwargs={'pk': self.live5.pk})
        response = self.client.get(url, content_type='application/json')

        # Validate status code
        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)

    def test_retrieve_live_video_with_user_1(self):
        live2 = LiveVideoSerializer(self.live2).data
        self.client.login(username='user1', password='12345678')

        url = reverse('live-videos-detail', kwargs={'pk': self.live2.pk})
        response = self.client.get(url, content_type='application/json')

        # Validate status code
        self.assertEqual(status.HTTP_200_OK, response.status_code)

        # Validate live_video
        self.assertEqual(live2, response.data)

    def test_retrieve_live_video_with_user_2(self):
        live4 = LiveVideoSerializer(self.live4).data
        self.client.login(username='user2', password='12345678')

        url = reverse('live-videos-detail', kwargs={'pk': self.live4.pk})
        response = self.client.get(url, content_type='application/json')

        # Validate status code
        self.assertEqual(status.HTTP_200_OK, response.status_code)

        # Validate live_video
        self.assertEqual(live4, response.data)

    def test_retrieve_live_video_with_key(self):
        live2 = LiveVideoSerializer(self.live2).data

        url1 = reverse('live-videos-detail', kwargs={'pk': self.live2.pk})
        url2 = reverse('live-videos-detail', kwargs={'pk': self.live5.pk})
        header = {'HTTP_AUTHORIZATION': self.key.api_key}
        response1 = self.client.get(
            url1, content_type='application/json', **header
        )
        response2 = self.client.get(
            url2, content_type='application/json', **header
        )

        # Validate status code
        self.assertEqual(status.HTTP_200_OK, response1.status_code)
        self.assertEqual(status.HTTP_404_NOT_FOUND, response2.status_code)

        # Validate live_video
        self.assertEqual(live2, response1.data)

    # </editor-fold>

    # <editor-fold desc="Put LiveVideo TESTS">
    def test_put_live_video_annon_user(self):
        data = {
            "name": "foo",
            "channel": self.chan3.pk,
            "tags": [self.tag1.name, self.tag2.name],
            "ads_vast_url": None,
            "enable_ads": True,
        }

        url = reverse('live-videos-detail', kwargs={'pk': self.live1.pk})
        response = self.client.put(url, data=data, format='json')

        # Validate status code
        self.assertEqual(status.HTTP_401_UNAUTHORIZED, response.status_code)

    def test_put_live_video_with_multiple_channels(self):
        data = {
            "name": "foo",
            "channel": [self.chan1.pk, self.chan2.pk, self.chan3.pk],
            "tags": [self.tag1.name, self.tag2.name],
        }
        self.client.login(username='user1', password='12345678')

        url = reverse('live-videos-detail', kwargs={'pk': self.live2.pk})
        response = self.client.put(url, data=data, format='json')

        # Validate status code
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)

    def test_put_live_video_with_superuser_with_org_1(self):
        data = {
            "name": "foo",
            "channel": self.chan2.pk,
            "tags": [self.tag1.name, self.tag2.name],
            "ads_vast_url": None,
            "enable_ads": True,
        }

        self.client.login(username='admin', password='12345678')

        url = reverse('live-videos-detail', kwargs={'pk': self.live1.pk})
        response = self.client.put(url, data=data, format='json')

        # Validate status code
        self.assertEqual(status.HTTP_200_OK, response.status_code)

        # Validate channels
        self.assertEqual(data['channel'], response.json()['channel'])

        # Validate tags
        self.assertIn(data['tags'][0], response.json()['tags'])
        self.assertIn(data['tags'][1], response.json()['tags'])

        # Validate other fields
        self.assertEqual(data['name'], response.json()['name'])
        self.assertEqual(data['ads_vast_url'], response.json()['ads_vast_url'])
        self.assertEqual(data['enable_ads'], response.json()['enable_ads'])

    def test_put_live_video_with_user_from_different_org(self):
        data = {
            "name": "foo",
            "channel": self.chan5.pk,
            "tags": [self.tag3.name, self.tag4.name],
            "ads_vast_url": None,
            "enable_ads": True,
        }

        self.client.login(username='admin', password='12345678')

        url = reverse('live-videos-detail', kwargs={'pk': self.live5.pk})
        response = self.client.put(url, data=data, format='json')

        # Validate status code
        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)

    def test_put_live_video_with_user_1(self):
        data = {
            "name": "foo",
            "channel": self.chan1.pk,
            "tags": [self.tag1.name, self.tag2.name],
            "ads_vast_url": None,
            "enable_ads": True,
        }

        self.client.login(username='user1', password='12345678')

        url = reverse('live-videos-detail', kwargs={'pk': self.live2.pk})
        response = self.client.put(url, data=data, format='json')

        # Validate status code
        self.assertEqual(status.HTTP_200_OK, response.status_code)

        # Validate channels
        self.assertEqual(data['channel'], response.json()['channel'])

        # Validate tags
        self.assertIn(data['tags'][0], response.json()['tags'])
        self.assertIn(data['tags'][1], response.json()['tags'])

        # Validate other fields
        self.assertEqual(data['name'], response.json()['name'])
        self.assertEqual(data['ads_vast_url'], response.json()['ads_vast_url'])
        self.assertEqual(data['enable_ads'], response.json()['enable_ads'])

    def test_put_live_video_with_user_2(self):
        data = {
            "name": "foo",
            "channel": self.chan4.pk,
            "tags": [self.tag3.name, self.tag4.name],
            "ads_vast_url": None,
            "enable_ads": True,
        }
        self.client.login(username='user2', password='12345678')

        url = reverse('live-videos-detail', kwargs={'pk': self.live4.pk})
        response = self.client.put(url, data=data, format='json')

        # Validate status code
        self.assertEqual(status.HTTP_200_OK, response.status_code)

        # Validate channels
        self.assertEqual(data['channel'], response.json()['channel'])

        # Validate tags
        self.assertIn(data['tags'][0], response.json()['tags'])
        self.assertIn(data['tags'][1], response.json()['tags'])

        # Validate other fields
        self.assertEqual(data['name'], response.json()['name'])
        self.assertEqual(data['ads_vast_url'], response.json()['ads_vast_url'])
        self.assertEqual(data['enable_ads'], response.json()['enable_ads'])

    def test_put_live_video_with_key(self):
        data = {
            "name": "foo",
            "channel": self.chan1.pk,
            "tags": [self.tag1.name, self.tag2.name],
            "ads_vast_url": None,
            "enable_ads": True,
        }

        url1 = reverse('live-videos-detail', kwargs={'pk': self.live2.pk})
        url2 = reverse('live-videos-detail', kwargs={'pk': self.live5.pk})
        header = {'HTTP_AUTHORIZATION': self.key.api_key}
        response1 = self.client.put(url1, data=data, format='json', **header)
        response2 = self.client.put(url2, data=data, format='json', **header)

        # Validate status code
        self.assertEqual(status.HTTP_200_OK, response1.status_code)
        self.assertEqual(status.HTTP_404_NOT_FOUND, response2.status_code)

        # Validate channels
        self.assertEqual(data['channel'], response1.json()['channel'])

        # Validate tags
        self.assertIn(data['tags'][0], response1.json()['tags'])
        self.assertIn(data['tags'][1], response1.json()['tags'])

        # Validate other fields
        self.assertEqual(data['name'], response1.json()['name'])
        self.assertEqual(
            data['ads_vast_url'], response1.json()['ads_vast_url']
        )
        self.assertEqual(data['enable_ads'], response1.json()['enable_ads'])

    # </editor-fold>

    # <editor-fold desc="Patch LiveVideo TESTS">
    def test_patch_live_video_annon_user(self):
        url = reverse('live-videos-detail', kwargs={'pk': self.live1.pk})
        response = self.client.patch(url, content_type='application/json')

        # Validate status code
        self.assertEqual(status.HTTP_401_UNAUTHORIZED, response.status_code)

    def test_patch_live_video_with_multiple_channels(self):
        data = {"name": "New name", "channel": [self.chan1.pk, self.chan2.pk]}
        self.client.login(username='user1', password='12345678')

        url = reverse('live-videos-detail', kwargs={'pk': self.live1.pk})
        response = self.client.patch(url, data=data, format='json')

        # Validate status code
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)

    def test_patch_live_video_with_superuser_video_with_org_1(self):
        data = {
            "name": "New name",
            "channel": self.chan2.pk,
        }

        self.client.login(username='admin', password='12345678')

        url = reverse('live-videos-detail', kwargs={'pk': self.live1.pk})
        response = self.client.patch(url, data=data, format='json')

        # Validate status code
        self.assertEqual(status.HTTP_200_OK, response.status_code)

        # Validate name
        self.assertEqual(response.data["name"], data['name'])

        # Validate channels
        self.assertEqual(self.chan2.pk, response.json()['channel'])

    def test_patch_live_video_with_user_from_different_org(self):
        data = {
            "name": "New name",
            "channel": self.chan1.pk,
        }
        self.client.login(username='admin', password='12345678')

        url = reverse('live-videos-detail', kwargs={'pk': self.live4.pk})
        response = self.client.patch(url, data=data, format='json')

        # Validate status code
        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)

    def test_patch_live_video_with_user_1(self):
        data = {"tags": [self.tag1.pk], "channel": self.chan3.pk}
        self.client.login(username='user1', password='12345678')

        url = reverse('live-videos-detail', kwargs={'pk': self.live3.pk})
        response = self.client.patch(url, data=data, format='json')

        # Validate status code
        self.assertEqual(status.HTTP_200_OK, response.status_code)

        # Validate tags
        self.assertIn(str(self.tag1.pk), response.json()['tags'])
        self.assertNotIn(str(self.tag2.pk), response.json()['tags'])

        self.assertEqual(self.chan3.pk, response.json()['channel'])

    def test_patch_live_video_with_user_2(self):
        data = {
            "tags": [self.tag3.pk],
            "channel": self.chan5.pk,
        }
        self.client.login(username='user2', password='12345678')

        url = reverse('live-videos-detail', kwargs={'pk': self.live4.pk})
        response = self.client.patch(url, data=data, format='json')

        # Validate status code
        self.assertEqual(status.HTTP_200_OK, response.status_code)

        # Validate tags
        self.assertIn(str(self.tag3.pk), response.json()['tags'])
        self.assertNotIn(str(self.tag4.pk), response.json()['tags'])

        # Validate channels
        self.assertEqual(self.chan5.pk, response.json()['channel'])

    def test_patch_live_video_with_key(self):
        data = {"tags": [self.tag1.pk], "channel": self.chan3.pk}

        url1 = reverse('live-videos-detail', kwargs={'pk': self.live3.pk})
        url2 = reverse('live-videos-detail', kwargs={'pk': self.live4.pk})
        header = {'HTTP_AUTHORIZATION': self.key.api_key}
        response1 = self.client.patch(url1, data=data, format='json', **header)
        response2 = self.client.patch(url2, data=data, format='json', **header)

        # Validate status code
        self.assertEqual(status.HTTP_200_OK, response1.status_code)
        self.assertEqual(status.HTTP_404_NOT_FOUND, response2.status_code)

        # Validate tags
        self.assertIn(str(self.tag1.pk), response1.json()['tags'])
        self.assertNotIn(str(self.tag2.pk), response1.json()['tags'])

        self.assertEqual(self.chan3.pk, response1.json()['channel'])

    def test_patch_live_video_without_channels(self):
        data = {"tags": [self.tag3.pk]}
        self.client.login(username='user2', password='12345678')

        url = reverse('live-videos-detail', kwargs={'pk': self.live4.pk})
        response = self.client.patch(url, data=data, format='json')

        # Validate status code
        self.assertEqual(status.HTTP_200_OK, response.status_code)

        # Validate tags
        self.assertNotIn(str(self.tag1.pk), response.json()['tags'])
        self.assertNotIn(str(self.tag2.pk), response.json()['tags'])
        self.assertIn(str(self.tag3.pk), response.json()['tags'])
        self.assertNotIn(str(self.tag4.pk), response.json()['tags'])

    # </editor-fold>

    # <editor-fold desc="Create LiveVideo TESTS">
    def test_create_live_video_with_annon_user(self):
        data = {
            "name": "foo",
            "channel": self.chan2.pk,
            "tags": [self.tag1.name, self.tag2.name],
            "ads_vast_url": None,
            "enable_ads": True,
        }

        url = reverse('live-videos-list')
        response = self.client.post(url, data=data, format='json')

        # Validate status code
        self.assertEqual(status.HTTP_401_UNAUTHORIZED, response.status_code)

    def test_create_live_video_with_user_1(self):
        data = {
            "name": "foo",
            "channel": self.chan1.pk,
            "tags": [self.tag1.name, self.tag2.name],
            "ads_vast_url": None,
            "enable_ads": True,
        }

        self.client.login(username='user1', password='12345678')

        url = reverse('live-videos-list')
        response = self.client.post(url, data=data, format='json')

        # Validate status code
        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)

    def test_create_live_video_with_user_2(self):
        data = {
            "name": "foo",
            "channel": self.chan4.pk,
            "tags": [self.tag3.name, self.tag4.name],
            "ads_vast_url": None,
            "enable_ads": True,
        }

        self.client.login(username='user2', password='12345678')

        url = reverse('live-videos-list')
        response = self.client.post(url, data=data, format='json')

        # Validate status code
        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)

    def test_create_live_video_with_superuser(self):
        data = {
            "name": "foo",
            "channel": self.chan2.pk,
            "tags": [self.tag1.name, self.tag2.name],
            "ads_vast_url": None,
            "enable_ads": True,
        }

        self.client.login(username='admin', password='12345678')

        url = reverse('live-videos-list')
        response = self.client.post(url, data=data, format='json')

        # Validate status code
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)

    def test_create_live_video_with_key(self):
        data = {
            "name": "foo",
            "channel": self.chan1.pk,
            "tags": [self.tag1.name, self.tag2.name],
            "ads_vast_url": None,
            "enable_ads": True,
        }

        url = reverse('live-videos-list')
        header = {'HTTP_AUTHORIZATION': self.key.api_key}
        response = self.client.post(url, data=data, format='json', **header)

        # Validate status code
        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)

    # </editor-fold>

    # <editor-fold desc="Delete LiveVideo TESTS">
    def test_delete_live_video_with_annon_user(self):
        url = reverse('live-videos-detail', kwargs={'pk': self.live1.pk})
        response = self.client.delete(url, content_type='application/json')

        # Validate status code
        self.assertEqual(status.HTTP_401_UNAUTHORIZED, response.status_code)

    def test_delete_live_video_with_superuser_with_org_1(self):
        self.client.login(username='admin', password='12345678')

        url = reverse('live-videos-detail', kwargs={'pk': self.live1.pk})
        response = self.client.delete(url, content_type='application/json')

        # Validate status code
        self.assertEqual(status.HTTP_204_NO_CONTENT, response.status_code)

    def test_delete_live_video_with_user_from_different_org(self):
        self.client.login(username='admin', password='12345678')

        url = reverse('live-videos-detail', kwargs={'pk': self.live5.pk})
        response = self.client.delete(url, content_type='application/json')

        # Validate status code
        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)

    def test_delete_live_video_with_user_1(self):
        self.client.login(username='user1', password='12345678')

        url = reverse('live-videos-detail', kwargs={'pk': self.live1.pk})
        response = self.client.delete(url, content_type='application/json')

        # Validate status code
        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)

    def test_delete_live_video_with_user_2(self):
        self.client.login(username='user2', password='12345678')

        url = reverse('live-videos-detail', kwargs={'pk': self.live1.pk})
        response = self.client.delete(url, content_type='application/json')

        # Validate status code
        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)

    def test_delete_live_video_with_key(self):
        self.client.login(username='user1', password='12345678')

        url1 = reverse('live-videos-detail', kwargs={'pk': self.live1.pk})
        url2 = reverse('live-videos-detail', kwargs={'pk': self.live5.pk})
        header = {'HTTP_AUTHORIZATION': self.key.api_key}
        response1 = self.client.delete(
            url1, content_type='application/json', **header
        )
        response2 = self.client.delete(
            url2, content_type='application/json', **header
        )

        # Validate status code
        self.assertEqual(status.HTTP_403_FORBIDDEN, response1.status_code)
        self.assertEqual(status.HTTP_403_FORBIDDEN, response2.status_code)

    # </editor-fold>

    # <editor-fold desc="Transition by API LiveVideo TESTS">
    def test_change_live_video_status_from_starting_to_stopping_with_user_1_org_1(
        self,
    ):
        live_starting = create_live_video(
            'Video', self.user1, self.org1, 1, LiveVideo.State.STARTING
        )

        self.client.login(username='user1', password='12345678')

        url = reverse('live-videos-to-off', kwargs={'pk': live_starting.pk})
        with mock.patch('utils.medialive.stop_channel', side_effect=None):
            response = self.client.post(url, data=None, format=None)

        # Validate status code
        self.assertEqual(status.HTTP_200_OK, response.status_code)

        live_starting_updated = LiveVideo.objects.get(id=live_starting.pk)

        # Validate live_video state
        self.assertEqual(LiveVideo.State.STOPPING, live_starting_updated.state)

    def test_change_live_video_status_from_stopping_to_stopping_with_user_1_org_1(
        self,
    ):
        live_stopping = create_live_video(
            'Video', self.user1, self.org1, 1, LiveVideo.State.STOPPING
        )

        self.client.login(username='user1', password='12345678')

        url = reverse('live-videos-to-off', kwargs={'pk': live_stopping.pk})
        with mock.patch('utils.medialive.stop_channel', side_effect=None):
            response = self.client.post(url, data=None, format=None)

        # Validate status code
        self.assertEqual(status.HTTP_200_OK, response.status_code)

        live_stopping_updated = LiveVideo.objects.get(id=live_stopping.pk)

        # Validate live_video state
        self.assertEqual(LiveVideo.State.STOPPING, live_stopping_updated.state)

    def test_change_live_video_status_from_on_to_stopping_with_user_1_org_1(
        self,
    ):
        live_on = create_live_video(
            'Video', self.user1, self.org1, 1, LiveVideo.State.ON
        )

        self.client.login(username='user1', password='12345678')

        url = reverse('live-videos-to-off', kwargs={'pk': live_on.pk})
        with mock.patch('utils.medialive.stop_channel', side_effect=None):
            response = self.client.post(url, data=None, format=None)

        # Validate status code
        self.assertEqual(status.HTTP_200_OK, response.status_code)

        live_on_updated = LiveVideo.objects.get(id=live_on.pk)

        # Validate live_video state
        self.assertEqual(LiveVideo.State.STOPPING, live_on_updated.state)

    def test_change_live_video_status_from_off_to_stopping_with_user_1_org_1(
        self,
    ):
        live_off = create_live_video(
            'Video', self.user1, self.org1, 1, LiveVideo.State.OFF
        )

        self.client.login(username='user1', password='12345678')

        url = reverse('live-videos-to-off', kwargs={'pk': live_off.pk})
        with mock.patch('utils.medialive.stop_channel', side_effect=None):
            response = self.client.post(url, data=None, format=None)

        # Validate status code
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)

    def test_change_live_video_status_from_stopping_to_starting_with_user_1_org_1(
        self,
    ):
        live_stopping = create_live_video(
            'Video', self.user1, self.org1, 1, LiveVideo.State.STOPPING
        )

        self.client.login(username='user1', password='12345678')

        url = reverse('live-videos-to-on', kwargs={'pk': live_stopping.pk})
        with mock.patch('utils.medialive.start_channel', side_effect=None):
            response = self.client.post(url, data=None, format=None)

        # Validate status code
        self.assertEqual(status.HTTP_200_OK, response.status_code)

        live_stopping_updated = LiveVideo.objects.get(id=live_stopping.pk)

        # Validate live_video state
        self.assertEqual(LiveVideo.State.STARTING, live_stopping_updated.state)

    def test_change_live_video_status_from_starting_to_starting_with_user_1_org_1(
        self,
    ):
        live_starting = create_live_video(
            'Video', self.user1, self.org1, 1, LiveVideo.State.STARTING
        )

        self.client.login(username='user1', password='12345678')

        url = reverse('live-videos-to-on', kwargs={'pk': live_starting.pk})
        with mock.patch('utils.medialive.start_channel', side_effect=None):
            response = self.client.post(url, data=None, format=None)

        # Validate status code
        self.assertEqual(status.HTTP_200_OK, response.status_code)

        live_starting_updated = LiveVideo.objects.get(id=live_starting.pk)

        # Validate live_video state
        self.assertEqual(LiveVideo.State.STARTING, live_starting_updated.state)

    def test_change_live_video_status_from_off_to_starting_with_user_1_org_1(
        self,
    ):
        live_off = create_live_video(
            'Video', self.user1, self.org1, 1, LiveVideo.State.OFF
        )

        self.client.login(username='user1', password='12345678')

        url = reverse('live-videos-to-on', kwargs={'pk': live_off.pk})
        with mock.patch('utils.medialive.start_channel', side_effect=None):
            response = self.client.post(url, data=None, format=None)

        # Validate status code
        self.assertEqual(status.HTTP_200_OK, response.status_code)

        live_off_updated = LiveVideo.objects.get(id=live_off.pk)

        # Validate live_video state
        self.assertEqual(LiveVideo.State.STARTING, live_off_updated.state)

    def test_change_live_video_status_from_on_to_starting_with_user_1_org_1(
        self,
    ):
        live_on = create_live_video(
            'Video', self.user1, self.org1, 1, LiveVideo.State.ON
        )

        self.client.login(username='user1', password='12345678')

        url = reverse('live-videos-to-on', kwargs={'pk': live_on.pk})
        with mock.patch('utils.medialive.start_channel', side_effect=None):
            response = self.client.post(url, data=None, format=None)

        # Validate status code
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)

    # </editor-fold>

    # <editor-fold desc="Alerts endpoints LiveVideo TESTS">
    def test_subscribe_to_alerts_with_annon_user(self):
        data = {
            "video_id": self.live1.video_id,
            "endpoint_http": "http://prueba.com",
        }
        arn = 'mocked_subscription_arn'

        url = reverse('live-videos-subscribe')
        with mock.patch('utils.sns.subscribe', return_value=arn):
            response = self.client.post(url, data=data, format='json')

        # Validate status code
        self.assertEqual(status.HTTP_401_UNAUTHORIZED, response.status_code)

    def test_subscribe_to_alerts_if_no_live(self):
        data = {
            "video_id": "videoid",
            "endpoint_http": "http://prueba.com",
        }
        arn = 'mocked_subscription_arn'

        self.client.login(username='user1', password='12345678')

        url = reverse('live-videos-subscribe')
        with mock.patch('utils.sns.subscribe', return_value=arn):
            response = self.client.post(url, data=data, format='json')

            # Validate status code
            self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)

    def test_subscribe_to_alerts_with_user_1_org_1(self):
        live_sub = create_live_video(
            'Video', self.user1, self.org1, 1, ml_channel_arn='probando'
        )

        data = {
            "video_id": live_sub.video_id,
            "endpoint_http": "http://prueba.com",
        }
        arn = 'mocked_subscription_arn'

        self.client.login(username='user1', password='12345678')

        url = reverse('live-videos-subscribe')
        with mock.patch('utils.sns.subscribe', return_value=arn):
            response = self.client.post(url, data=data, format='json')

        # Validate status code
        self.assertEqual(status.HTTP_200_OK, response.status_code)

        # Validate subscription
        self.assertEqual(arn, response.json()['subscription_id'])
        self.assertEqual(
            live_sub.ml_channel_arn, response.json()['channel_arn']
        )

    def test_subscribe_to_alert_no_subscription_created(self):
        data = {
            "video_id": self.live1.video_id,
            "endpoint_http": "http://prueba.com",
        }

        self.client.login(username='user1', password='12345678')

        url = reverse('live-videos-subscribe')
        with mock.patch(
            'utils.sns.subscribe',
            side_effect=sns.NotificationNotFoundException(),
        ):
            response = self.client.post(url, data=data, format='json')

        # Validate status code
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)

        # Validate response detail
        self.assertEqual(
            'Could not subscribe to alert service', response.data['detail']
        )

    def test_notify_alerts_confirm_subscription(self):
        data = {"SubscribeURL": "http://prueba.com"}

        url = reverse('live-videos-notify')
        with mock.patch('requests.get', side_effect=None):
            headers = {
                'HTTP_X_AMZ_SNS_MESSAGE_TYPE': 'SubscriptionConfirmation'
            }
            response = self.client.post(
                url, data=data, format='json', **headers
            )

        # Validate status code
        self.assertEqual(status.HTTP_200_OK, response.status_code)

    def test_notify_alerts_if_no_live(self):
        msg = {
            "alarm_state": "SET",
            "alert_type": "Video Not Detected",
            "channel_arn": "channelarn",
        }

        data = {"Message": json.dumps(msg)}

        url = reverse('live-videos-notify')
        headers = {'HTTP_X_AMZ_SNS_MESSAGE_TYPE': 'Notification'}
        response = self.client.post(url, data=data, format='json', **headers)

        # Validate status code
        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)

    def test_notify_alerts_set_error_msg(self):
        live = create_live_video(
            'Video', self.user1, self.org1, 1, ml_channel_arn='probando'
        )

        msg = {
            "alarm_state": "SET",
            "alert_type": "Video Not Detected",
            "channel_arn": live.ml_channel_arn,
        }

        data = {"Message": json.dumps(msg)}

        url = reverse('live-videos-notify')
        headers = {'HTTP_X_AMZ_SNS_MESSAGE_TYPE': 'Notification'}
        response = self.client.post(url, data=data, format='json', **headers)

        # Validate status code
        self.assertEqual(status.HTTP_200_OK, response.status_code)

        # Update live
        live = LiveVideo.objects.get(id=live.pk)

        # Validate set live input state
        self.assertIn(msg['alert_type'], live.input_state)

    def test_notify_alerts_clear_error_msg(self):
        live = create_live_video(
            'Video',
            self.user1,
            self.org1,
            1,
            ml_channel_arn='testing',
            input_state=['Video Not Detected'],
        )
        msg = {
            "alarm_state": "CLEARED",
            "alert_type": "Video Not Detected",
            "channel_arn": live.ml_channel_arn,
        }

        data = {"Message": json.dumps(msg)}

        url = reverse('live-videos-notify')
        headers = {'HTTP_X_AMZ_SNS_MESSAGE_TYPE': 'Notification'}
        response = self.client.post(url, data=data, format='json', **headers)

        # Validate status code
        self.assertEqual(status.HTTP_200_OK, response.status_code)

        # Update live
        live = LiveVideo.objects.get(id=live.pk)

        # Validate clear live input state
        self.assertNotIn(msg['alert_type'], live.input_state)

    # </editor-fold>

    # <editor-fold desc="Check LiveVideo Status TESTS">
    class MockMediaLive:
        def __init__(self, state, raise_exception=False):
            self.state = state
            self.raise_exception = raise_exception

        def describe_channel(self, *args, **kwargs):
            if self.raise_exception:
                raise Exception()

            return {
                'State': self.state,
                'Destinations': [
                    {
                        'Settings': [
                            {
                                'Url': 's3://organization/live/input-id-as-key/output'
                            }
                        ]
                    }
                ],
            }

    def test_check_live_status_starting_with_running_in_aws(self):
        live_starting = create_live_video(
            'Video', self.user1, self.org1, 1, LiveVideo.State.STARTING
        )

        with mock.patch(
            'utils.medialive.get_media_live',
            return_value=self.MockMediaLive('RUNNING'),
        ):
            medialive.check_live_state(live_starting.video_id)

        live_starting_updated = LiveVideo.objects.get(id=live_starting.pk)

        # Validate live_video state
        self.assertEqual(LiveVideo.State.ON, live_starting_updated.state)

    def test_check_live_status_starting_with_idle_in_aws(self):
        live_starting = create_live_video(
            'Video', self.user1, self.org1, 1, LiveVideo.State.STARTING
        )

        with self.assertRaises(TransitionNotAllowed):
            with mock.patch(
                'utils.medialive.get_media_live',
                return_value=self.MockMediaLive('IDLE'),
            ):
                with mock.patch(
                    'utils.medialive._delete_channel_storage', side_effect=None
                ):
                    medialive.check_live_state(live_starting.video_id)

    def test_check_live_status_starting_with_creating_in_aws(self):
        live_starting = create_live_video(
            'Video', self.user1, self.org1, 1, LiveVideo.State.STARTING
        )

        with mock.patch(
            'utils.medialive.get_media_live',
            return_value=self.MockMediaLive('CREATING'),
        ):
            medialive.check_live_state(live_starting.video_id)

        live_starting_updated = LiveVideo.objects.get(id=live_starting.pk)

        # Validate live_video state unchanged
        self.assertEqual(LiveVideo.State.STARTING, live_starting_updated.state)

    def test_check_live_status_starting_with_create_failed_in_aws(self):
        live_starting = create_live_video(
            'Video', self.user1, self.org1, 1, LiveVideo.State.STARTING
        )

        with mock.patch(
            'utils.medialive.get_media_live',
            return_value=self.MockMediaLive('CREATE_FAILED'),
        ):
            medialive.check_live_state(live_starting.video_id)

        live_starting_updated = LiveVideo.objects.get(id=live_starting.pk)

        # Validate live_video state unchanged
        self.assertEqual(LiveVideo.State.STARTING, live_starting_updated.state)

    def test_check_live_status_starting_with_recovering_in_aws(self):
        live_starting = create_live_video(
            'Video', self.user1, self.org1, 1, LiveVideo.State.STARTING
        )

        with mock.patch(
            'utils.medialive.get_media_live',
            return_value=self.MockMediaLive('RECOVERING'),
        ):
            medialive.check_live_state(live_starting.video_id)

        live_starting_updated = LiveVideo.objects.get(id=live_starting.pk)

        # Validate live_video state unchanged
        self.assertEqual(LiveVideo.State.STARTING, live_starting_updated.state)

    def test_check_live_status_starting_with_deleting_in_aws(self):
        live_starting = create_live_video(
            'Video', self.user1, self.org1, 1, LiveVideo.State.STARTING
        )

        with mock.patch(
            'utils.medialive.get_media_live',
            return_value=self.MockMediaLive('DELETING'),
        ):
            medialive.check_live_state(live_starting.video_id)

        live_starting_updated = LiveVideo.objects.get(id=live_starting.pk)

        # Validate live_video state unchanged
        self.assertEqual(LiveVideo.State.STARTING, live_starting_updated.state)

    def test_check_live_status_starting_with_deleted_in_aws(self):
        live_starting = create_live_video(
            'Video', self.user1, self.org1, 1, LiveVideo.State.STARTING
        )

        with mock.patch(
            'utils.medialive.get_media_live',
            return_value=self.MockMediaLive('DELETED'),
        ):
            medialive.check_live_state(live_starting.video_id)

        live_starting_updated = LiveVideo.objects.get(id=live_starting.pk)

        # Validate live_video state unchanged
        self.assertEqual(LiveVideo.State.STARTING, live_starting_updated.state)

    def test_check_live_status_starting_with_starting_in_aws(self):
        live_starting = create_live_video(
            'Video', self.user1, self.org1, 1, LiveVideo.State.STARTING
        )

        with mock.patch(
            'utils.medialive.get_media_live',
            return_value=self.MockMediaLive('STARTING'),
        ):
            medialive.check_live_state(live_starting.video_id)

        live_starting_updated = LiveVideo.objects.get(id=live_starting.pk)

        # Validate live_video state unchanged
        self.assertEqual(LiveVideo.State.STARTING, live_starting_updated.state)

    def test_check_live_status_starting_with_stopping_in_aws(self):
        live_starting = create_live_video(
            'Video', self.user1, self.org1, 1, LiveVideo.State.STARTING
        )

        with mock.patch(
            'utils.medialive.get_media_live',
            return_value=self.MockMediaLive('STOPPING'),
        ):
            medialive.check_live_state(live_starting.video_id)

        live_starting_updated = LiveVideo.objects.get(id=live_starting.pk)

        # Validate live_video state unchanged
        self.assertEqual(LiveVideo.State.STARTING, live_starting_updated.state)

    def test_check_live_status_stopping_with_running_in_aws(self):
        live_stopping = create_live_video(
            'Video', self.user1, self.org1, 1, LiveVideo.State.STOPPING
        )

        with self.assertRaises(TransitionNotAllowed):
            with mock.patch(
                'utils.medialive.get_media_live',
                return_value=self.MockMediaLive('RUNNING'),
            ):
                medialive.check_live_state(live_stopping.video_id)

    def test_check_live_status_stopping_with_idle_in_aws(self):
        live_stopping = create_live_video(
            'Video', self.user1, self.org1, 1, LiveVideo.State.STOPPING
        )

        with mock.patch(
            'utils.medialive.get_media_live',
            return_value=self.MockMediaLive('IDLE'),
        ):
            with mock.patch(
                'utils.medialive._delete_channel_storage', side_effect=None
            ):
                medialive.check_live_state(live_stopping.video_id)

        live_stopping_updated = LiveVideo.objects.get(id=live_stopping.pk)

        # Validate live_video state unchanged
        self.assertEqual(LiveVideo.State.OFF, live_stopping_updated.state)

    def test_check_live_status_stopping_with_creating_in_aws(self):
        live_stopping = create_live_video(
            'Video', self.user1, self.org1, 1, LiveVideo.State.STOPPING
        )

        with mock.patch(
            'utils.medialive.get_media_live',
            return_value=self.MockMediaLive('CREATING'),
        ):
            medialive.check_live_state(live_stopping.video_id)

        live_stopping_updated = LiveVideo.objects.get(id=live_stopping.pk)

        # Validate live_video state unchanged
        self.assertEqual(LiveVideo.State.STOPPING, live_stopping_updated.state)

    def test_check_live_status_stopping_with_create_failed_in_aws(self):
        live_stopping = create_live_video(
            'Video', self.user1, self.org1, 1, LiveVideo.State.STOPPING
        )

        with mock.patch(
            'utils.medialive.get_media_live',
            return_value=self.MockMediaLive('CREATE_FAILED'),
        ):
            medialive.check_live_state(live_stopping.video_id)

        live_stopping_updated = LiveVideo.objects.get(id=live_stopping.pk)

        # Validate live_video state unchanged
        self.assertEqual(LiveVideo.State.STOPPING, live_stopping_updated.state)

    def test_check_live_status_stopping_with_recovering_in_aws(self):
        live_stopping = create_live_video(
            'Video', self.user1, self.org1, 1, LiveVideo.State.STOPPING
        )

        with mock.patch(
            'utils.medialive.get_media_live',
            return_value=self.MockMediaLive('RECOVERING'),
        ):
            medialive.check_live_state(live_stopping.video_id)

        live_stopping_updated = LiveVideo.objects.get(id=live_stopping.pk)

        # Validate live_video state unchanged
        self.assertEqual(LiveVideo.State.STOPPING, live_stopping_updated.state)

    def test_check_live_status_stopping_with_deleting_in_aws(self):
        live_stopping = create_live_video(
            'Video', self.user1, self.org1, 1, LiveVideo.State.STOPPING
        )

        with mock.patch(
            'utils.medialive.get_media_live',
            return_value=self.MockMediaLive('DELETING'),
        ):
            medialive.check_live_state(live_stopping.video_id)

        live_stopping_updated = LiveVideo.objects.get(id=live_stopping.pk)

        # Validate live_video state unchanged
        self.assertEqual(LiveVideo.State.STOPPING, live_stopping_updated.state)

    def test_check_live_status_stopping_with_deleted_in_aws(self):
        live_stopping = create_live_video(
            'Video', self.user1, self.org1, 1, LiveVideo.State.STOPPING
        )

        with mock.patch(
            'utils.medialive.get_media_live',
            return_value=self.MockMediaLive('DELETED'),
        ):
            medialive.check_live_state(live_stopping.video_id)

        live_stopping_updated = LiveVideo.objects.get(id=live_stopping.pk)

        # Validate live_video state unchanged
        self.assertEqual(LiveVideo.State.STOPPING, live_stopping_updated.state)

    def test_check_live_status_stopping_with_starting_in_aws(self):
        live_stopping = create_live_video(
            'Video', self.user1, self.org1, 1, LiveVideo.State.STOPPING
        )

        with mock.patch(
            'utils.medialive.get_media_live',
            return_value=self.MockMediaLive('STARTING'),
        ):
            medialive.check_live_state(live_stopping.video_id)

        live_stopping_updated = LiveVideo.objects.get(id=live_stopping.pk)

        # Validate live_video state unchanged
        self.assertEqual(LiveVideo.State.STOPPING, live_stopping_updated.state)

    def test_check_live_status_stopping_with_stopping_in_aws(self):
        live_stopping = create_live_video(
            'Video', self.user1, self.org1, 1, LiveVideo.State.STOPPING
        )

        with mock.patch(
            'utils.medialive.get_media_live',
            return_value=self.MockMediaLive('STOPPING'),
        ):
            medialive.check_live_state(live_stopping.video_id)

        live_stopping_updated = LiveVideo.objects.get(id=live_stopping.pk)

        # Validate live_video state unchanged
        self.assertEqual(LiveVideo.State.STOPPING, live_stopping_updated.state)

    # </editor-fold>

    # <editor-fold desc="Search LiveVideo TESTS">
    def test_search_fields_by_name(self):
        self.client.login(username='admin', password='12345678')

        url = reverse('live-videos-list') + "?search=" + quote(self.live1.name)
        response = self.client.get(url, data=None, format=None)

        live1 = LiveVideoSerializer(self.live1).data

        # Validate status code
        self.assertEqual(status.HTTP_200_OK, response.status_code)

        # Validate live_videos in results
        self.assertIn(live1, response.json()['results'])

    def test_search_fields_by_tag(self):
        self.client.login(username='user1', password='12345678')

        self.live1.tags.add(self.tag1)

        live1 = LiveVideoSerializer(self.live1).data

        url = reverse('live-videos-list') + "?search=" + quote(self.tag1.name)
        response = self.client.get(url, data=None, format=None)

        # Validate status code
        self.assertEqual(status.HTTP_200_OK, response.status_code)

        # Validate live_videos in results
        self.assertEqual(1, len(response.json()['results']))
        self.assertIn(live1, response.json()['results'])

    def test_search_fields_by_id(self):
        self.client.login(username='user2', password='12345678')

        live1 = LiveVideoSerializer(self.live1).data
        live2 = LiveVideoSerializer(self.live2).data
        live3 = LiveVideoSerializer(self.live3).data
        live4 = LiveVideoSerializer(self.live4).data
        live5 = LiveVideoSerializer(self.live5).data

        url = (
            reverse('live-videos-list') + "?search=" + str(self.live4.video_id)
        )
        response = self.client.get(url, data=None, format=None)

        # Validate status code
        self.assertEqual(status.HTTP_200_OK, response.status_code)

        # Validate live_videos in results
        self.assertNotIn(live1, response.json()['results'])
        self.assertNotIn(live2, response.json()['results'])
        self.assertNotIn(live3, response.json()['results'])
        self.assertIn(live4, response.json()['results'])
        self.assertNotIn(live5, response.json()['results'])

    def test_search_fields_by_created_by(self):
        self.client.login(username='user1', password='12345678')

        live1 = LiveVideoSerializer(self.live1).data
        live2 = LiveVideoSerializer(self.live2).data
        live3 = LiveVideoSerializer(self.live3).data
        live4 = LiveVideoSerializer(self.live4).data
        live5 = LiveVideoSerializer(self.live5).data

        url = (
            reverse('live-videos-list')
            + "?search="
            + quote(self.user1.username)
        )
        response = self.client.get(url, data=None, format=None)

        # Validate status code
        self.assertEqual(status.HTTP_200_OK, response.status_code)

        # Validate live_videos in results
        self.assertIn(live1, response.json()['results'])
        self.assertIn(live2, response.json()['results'])
        self.assertIn(live3, response.json()['results'])
        self.assertNotIn(live4, response.json()['results'])
        self.assertNotIn(live5, response.json()['results'])

    def test_search_fields_by_no_results(self):
        self.client.login(username='admin', password='12345678')

        url = reverse('live-videos-list') + "?search=asdf1234"
        response = self.client.get(url, data=None, format=None)

        live1 = LiveVideoSerializer(self.live1).data

        # Validate status code
        self.assertEqual(status.HTTP_200_OK, response.status_code)

        # Validate live_videos in results
        self.assertNotIn(live1, response.json()['results'])

    # </editor-fold>

    # <editor-fold desc="Geolocation LiveVideo TESTS">
    def test_live_video_without_geolocation_restriction(self):
        live_video = create_live_video('Video', self.user2, self.org2, 1)

        self.client.login(username='user2', password='12345678')

        url = reverse('live-videos-detail', kwargs={'pk': live_video.pk})
        response = self.client.get(url, data=None, format=None)

        # Validate status code
        self.assertEqual(status.HTTP_200_OK, response.status_code)

        # Validate video with no Restriction
        self.assertEqual(
            LiveVideo.GeoType.NONE, response.json()['geolocation_type']
        )
        self.assertEqual([], response.json()['geolocation_countries'])

    def test_live_video_with_whitelist_geolocation_restriction(self):
        live_video = create_live_video('Video', self.user2, self.org2, 1)
        add_channel_to_live_video(self.chan4, live_video)

        self.client.login(username='user2', password='12345678')

        data = {
            "geolocation_type": "whitelist",
            "geolocation_countries": ['UY', 'AR', 'ZA'],
        }

        url = reverse('live-videos-detail', kwargs={'pk': live_video.pk})
        response = self.client.patch(url, data=data, format='json')

        # Validate status code
        self.assertEqual(status.HTTP_200_OK, response.status_code)

        # Validate video with whitelist restriction
        self.assertEqual(
            data['geolocation_type'], response.json()['geolocation_type']
        )
        self.assertEqual(
            data['geolocation_countries'],
            response.json()['geolocation_countries'],
        )

    def test_live_video_with_blacklist_geolocation_restriction(self):
        live_video = create_live_video('Video 1', self.user1, self.org1, 1)
        add_channel_to_live_video(self.chan1, live_video)

        self.client.login(username='user1', password='12345678')

        data = {
            "name": "New Restriction",
            "geolocation_type": "blacklist",
            "geolocation_countries": ['CL', 'PY', 'TN'],
        }

        url = reverse('live-videos-detail', kwargs={'pk': live_video.pk})
        response = self.client.patch(url, data=data, format='json')

        # Validate status code
        self.assertEqual(status.HTTP_200_OK, response.status_code)

        # Validate video with blacklist restriction
        self.assertEqual(
            data['geolocation_type'], response.json()['geolocation_type']
        )
        self.assertEqual(
            data['geolocation_countries'],
            response.json()['geolocation_countries'],
        )

    def test_live_video_geolocation_change_type_to_no_restriction(self):
        """
        Pre condiciones: geolocation restriction setted with list of countries
        Accion: change geolocation_type so there is not restriction
        Pos condiciones: geolocation_type = none and geolocation_countries unchanged
        """
        live_video = create_live_video('Video 1', self.user1, self.org1, 1)

        self.client.login(username='user1', password='12345678')

        data = {
            "channel": self.chan2.pk,
            "geolocation_type": "blacklist",
            "geolocation_countries": ['CL', 'PY', 'TN'],
        }

        url_1 = reverse('live-videos-detail', kwargs={'pk': live_video.pk})
        response = self.client.patch(url_1, data=data, format='json')

        # Validate status code
        self.assertEqual(status.HTTP_200_OK, response.status_code)

        new_data = {"geolocation_type": "none"}

        url = reverse('live-videos-detail', kwargs={'pk': live_video.pk})
        response = self.client.patch(url, data=new_data, format='json')

        # Validate status code
        self.assertEqual(status.HTTP_200_OK, response.status_code)

        # Validate geolocation restricition (no restriction)
        self.assertEqual(
            new_data['geolocation_type'], response.json()['geolocation_type']
        )
        self.assertEqual(
            data['geolocation_countries'],
            response.json()['geolocation_countries'],
        )

    # </editor-fold>
