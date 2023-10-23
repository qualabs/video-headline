import logging

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from organization.models import Organization
from test_utils import create_user, create_superuser, create_key, create_live_videos, \
    create_videos, create_channels, add_channel_to_video


class VideoLinkTests(APITestCase):

    @classmethod
    def setUpClass(cls):
        logging.disable(logging.WARNING)

        # Organizations
        cls.org1 = Organization.objects.create(name='Organization 1')
        cls.org2 = Organization.objects.create(name='Organization 2')

        # Channels
        cls.channels_org1 = create_channels('channel', cls.org1, 2, cf_domain='cf_domain1')
        cls.channels_org2 = create_channels('channel', cls.org2, 2, cf_domain='cf_domain2')

        # Users
        cls.user1 = create_user('user1', '12345678', cls.org1)
        cls.user2 = create_user('user2', '12345678', cls.org2)
        cls.su = create_superuser('admin', '12345678', cls.org1)
        cls.key = create_key('key', cls.user1)

    def setUp(self):
        # Videos
        self.video1, self.video3 = create_videos('Video', self.user1, self.org1, 2)
        add_channel_to_video(self.channels_org1[0], self.video1)
        add_channel_to_video(self.channels_org1[1], self.video3)

        self.video2, self.video4 = create_videos('Video', self.user2, self.org2, 2)
        add_channel_to_video(self.channels_org2[0], self.video2)
        add_channel_to_video(self.channels_org2[1], self.video4)

        # Lives
        self.live1 = create_live_videos('Live', self.user1, self.org1, 1)[0]
        self.live2 = create_live_videos('Live', self.user2, self.org2, 1)[0]

    @classmethod
    def tearDownClass(cls):
        logging.disable(logging.NOTSET)
        cls.org1.delete()
        cls.org2.delete()

    # <editor-fold desc="Get Video Link TESTS">
    def test_get_video_link_with_annon_user(self):
        url = reverse('link', kwargs={'video_id': self.video1.video_id})
        response = self.client.get(url, content_type='application/json')

        # Validate status code
        self.assertEqual(status.HTTP_401_UNAUTHORIZED, response.status_code)

    def test_get_video_link_with_superuser_with_org_1(self):
        self.client.login(username='admin', password='12345678')

        url = reverse('link', kwargs={'video_id': self.video1.video_id})
        response = self.client.get(url, content_type='application/json')

        video_url = {
            'video_url': self.video1.get_urls()[1],
            'type': 'application/x-mpegURL'
        }

        # Validate status code
        self.assertEqual(status.HTTP_200_OK, response.status_code)

        # Validate video link
        self.assertEqual(video_url, response.data)

    def test_get_video_link_with_user_from_different_org(self):
        self.client.login(username='admin', password='12345678')

        url = reverse('link', kwargs={'video_id': self.video2.video_id})
        response = self.client.get(url, content_type='application/json')

        # Validate status code
        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)

    def test_get_video_link_with_user_1(self):
        self.client.login(username='user1', password='12345678')

        url = reverse('link', kwargs={'video_id': self.video1.video_id})
        response = self.client.get(url, content_type='application/json')

        _, media_url, mime_type = self.video1.get_urls()

        video_url = {
            'video_url': media_url,
            'type': mime_type
        }

        # Validate status code
        self.assertEqual(status.HTTP_200_OK, response.status_code)

        # Validate video link
        self.assertEqual(video_url, response.data)

    def test_get_video_link_with_user_2(self):
        self.client.login(username='user2', password='12345678')

        url = reverse('link', kwargs={'video_id': self.video2.video_id})
        response = self.client.get(url, content_type='application/json')

        _, media_url, mime_type = self.video2.get_urls()

        video_url = {
            'video_url': media_url,
            'type': mime_type
        }

        # Validate status code
        self.assertEqual(status.HTTP_200_OK, response.status_code)

        # Validate video link
        self.assertEqual(video_url, response.data)

    def test_get_video_link_with_key(self):
        url1 = reverse('link', kwargs={'video_id': self.video1.video_id})
        url2 = reverse('link', kwargs={'video_id': self.video2.video_id})
        header = {'HTTP_AUTHORIZATION': self.key.api_key}
        response1 = self.client.get(url1, content_type='application/json', **header)
        response2 = self.client.get(url2, content_type='application/json', **header)

        _, media_url, mime_type = self.video1.get_urls()

        video_url = {
            'video_url': media_url,
            'type': mime_type
        }

        # Validate status code
        self.assertEqual(status.HTTP_200_OK, response1.status_code)
        self.assertEqual(status.HTTP_404_NOT_FOUND, response2.status_code)

        # Validate video link
        self.assertEqual(video_url, response1.data)

    # </editor-fold>

    # <editor-fold desc="Get Live Video Link TESTS">
    def test_get_live_video_link_with_annon_user(self):
        url = reverse('link', kwargs={'video_id': self.live1.video_id})
        response = self.client.get(url, content_type='application/json')

        # Validate status code
        self.assertEqual(status.HTTP_401_UNAUTHORIZED, response.status_code)

    def test_get_live_video_link_with_superuser_with_org_1(self):
        self.client.login(username='admin', password='12345678')

        url = reverse('link', kwargs={'video_id': self.live1.video_id})
        response = self.client.get(url, content_type='application/json')

        video_url = {
            'video_url': f'https://{self.live1.cf_domain}/output.m3u8',
            'type': 'application/x-mpegURL'
        }

        # Validate status code
        self.assertEqual(status.HTTP_200_OK, response.status_code)

        # Validate live video link
        self.assertEqual(video_url, response.data)

    def test_get_live_video_link_with_user_from_different_org(self):
        self.client.login(username='admin', password='12345678')

        url = reverse('link', kwargs={'video_id': self.live2.video_id})
        response = self.client.get(url, content_type='application/json')

        # Validate status code
        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)

    def test_get_live_video_link_with_user_1(self):
        self.client.login(username='user1', password='12345678')

        url = reverse('link', kwargs={'video_id': self.live1.video_id})
        response = self.client.get(url, content_type='application/json')

        video_url = {
            'video_url': f'https://{self.live1.cf_domain}/output.m3u8',
            'type': 'application/x-mpegURL'
        }

        # Validate status code
        self.assertEqual(status.HTTP_200_OK, response.status_code)

        # Validate video link
        self.assertEqual(video_url, response.data)

    def test_get_live_video_link_with_user_2(self):
        self.client.login(username='user2', password='12345678')

        url = reverse('link', kwargs={'video_id': self.live2.video_id})
        response = self.client.get(url, content_type='application/json')

        video_url = {
            'video_url': f'https://{self.live2.cf_domain}/output.m3u8',
            'type': 'application/x-mpegURL'
        }

        # Validate status code
        self.assertEqual(status.HTTP_200_OK, response.status_code)

        # Validate video link
        self.assertEqual(video_url, response.data)

    def test_get_live_video_link_with_key(self):
        url1 = reverse('link', kwargs={'video_id': self.live1.video_id})
        url2 = reverse('link', kwargs={'video_id': self.live2.video_id})
        header = {'HTTP_AUTHORIZATION': self.key.api_key}
        response1 = self.client.get(url1, content_type='application/json', **header)
        response2 = self.client.get(url2, content_type='application/json', **header)

        video_url = {
            'video_url': f'https://{self.live1.cf_domain}/output.m3u8',
            'type': 'application/x-mpegURL'
        }

        # Validate status code
        self.assertEqual(status.HTTP_200_OK, response1.status_code)
        self.assertEqual(status.HTTP_404_NOT_FOUND, response2.status_code)

        # Validate video link
        self.assertEqual(video_url, response1.data)
    # </editor-fold>
