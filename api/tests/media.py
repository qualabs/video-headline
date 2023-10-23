import logging
from unittest import mock

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from api.serializers.media import MediaSerializer
from test_utils import create_organizations, create_user, create_superuser, create_channels, \
    create_videos, create_tags, create_video, create_key
from video.models import Media


class VideoTests(APITestCase):

    @classmethod
    def setUpClass(cls):
        logging.disable(logging.WARNING)

        cls.org1, cls.org2 = create_organizations('Organization', 2)

        cls.user1 = create_user('user1', '12345678', cls.org1)
        cls.user2 = create_user('user2', '12345678', cls.org2)
        cls.su = create_superuser('admin', '12345678', cls.org1)
        cls.key = create_key('key', cls.user1)

        cls.chan1, cls.chan2, cls.chan3 = create_channels('Channel', cls.org1, 3)
        cls.chan4, cls.chan5 = create_channels('Channel', cls.org2, 2)

        cls.tag1 = create_tags('Funny tag', cls.org1, 1)[0]
        cls.tag2, cls.tag3 = create_tags('Funny tag', cls.org2, 2)

    def setUp(self):
        self.video1, self.video2, self.video3 = create_videos('Video', self.user1, self.org1, 3)
        self.video4, self.video5 = create_videos('Video', self.user2, self.org2, 2)

    def tearDown(self):
        Media.objects.all().delete()

    @classmethod
    def tearDownClass(cls):
        logging.disable(logging.NOTSET)
        cls.org1.delete()
        cls.org2.delete()

    # <editor-fold desc="List Video TESTS">
    def test_list_videos_with_annon_user(self):
        url = reverse('videos-list')
        response = self.client.get(url, format='json')

        # Validate status code
        self.assertEqual(status.HTTP_401_UNAUTHORIZED, response.status_code)

    def test_list_videos_with_superuser(self):
        video1 = MediaSerializer(self.video1).data
        video2 = MediaSerializer(self.video2).data
        video3 = MediaSerializer(self.video3).data
        video4 = MediaSerializer(self.video4).data
        video5 = MediaSerializer(self.video5).data

        self.client.login(username='admin', password='12345678')

        url = reverse('videos-list')
        response = self.client.get(url, format='json')

        # Validate status code
        self.assertEqual(status.HTTP_200_OK, response.status_code)

        # Validate videos in results
        self.assertIn(video1, response.json()['results'])
        self.assertIn(video2, response.json()['results'])
        self.assertIn(video3, response.json()['results'])
        self.assertNotIn(video4, response.json()['results'])
        self.assertNotIn(video5, response.json()['results'])

    def test_list_videos_with_user_1(self):
        video1 = MediaSerializer(self.video1).data
        video2 = MediaSerializer(self.video2).data
        video3 = MediaSerializer(self.video3).data
        video4 = MediaSerializer(self.video4).data
        video5 = MediaSerializer(self.video5).data

        self.client.login(username='user1', password='12345678')

        url = reverse('videos-list')
        response = self.client.get(url, format='json')

        # Validate status code
        self.assertEqual(status.HTTP_200_OK, response.status_code)

        # Validate videos in results
        self.assertIn(video1, response.json()['results'])
        self.assertIn(video2, response.json()['results'])
        self.assertIn(video3, response.json()['results'])
        self.assertNotIn(video4, response.json()['results'])
        self.assertNotIn(video5, response.json()['results'])

    def test_list_videos_with_user_2(self):
        video1 = MediaSerializer(self.video1).data
        video2 = MediaSerializer(self.video2).data
        video3 = MediaSerializer(self.video3).data
        video4 = MediaSerializer(self.video4).data
        video5 = MediaSerializer(self.video5).data

        self.client.login(username='user2', password='12345678')

        url = reverse('videos-list')
        response = self.client.get(url, format='json')

        # Validate status code
        self.assertEqual(status.HTTP_200_OK, response.status_code)

        # Validate videos in results
        self.assertNotIn(video1, response.json()['results'])
        self.assertNotIn(video2, response.json()['results'])
        self.assertNotIn(video3, response.json()['results'])
        self.assertIn(video4, response.json()['results'])
        self.assertIn(video5, response.json()['results'])

    def test_list_videos_with_key(self):
        video1 = MediaSerializer(self.video1).data
        video2 = MediaSerializer(self.video2).data
        video3 = MediaSerializer(self.video3).data
        video4 = MediaSerializer(self.video4).data
        video5 = MediaSerializer(self.video5).data

        url = reverse('videos-list')
        header = {'HTTP_AUTHORIZATION': self.key.api_key}
        response = self.client.get(url, format='json', **header)

        # Validate status code
        self.assertEqual(status.HTTP_200_OK, response.status_code)

        # Validate videos in results
        self.assertIn(video1, response.json()['results'])
        self.assertIn(video2, response.json()['results'])
        self.assertIn(video3, response.json()['results'])
        self.assertNotIn(video4, response.json()['results'])
        self.assertNotIn(video5, response.json()['results'])

    # </editor-fold>

    # <editor-fold desc="Retrieve Video TESTS">
    def test_retrieve_video_with_annon_user(self):
        url = reverse('videos-detail', kwargs={'pk': self.video1.pk})
        response = self.client.get(url, content_type='application/json')

        # Validate status code
        self.assertEqual(status.HTTP_401_UNAUTHORIZED, response.status_code)

    def test_retrieve_video_with_superuser_with_org_1(self):
        video1 = MediaSerializer(self.video1).data
        self.client.login(username='admin', password='12345678')

        url = reverse('videos-detail', kwargs={'pk': self.video1.pk})
        response = self.client.get(url, content_type='application/json')

        # Validate status code
        self.assertEqual(status.HTTP_200_OK, response.status_code)

        # Validate video
        self.assertEqual(video1, response.data)

    def test_retrieve_video_with_user_from_different_org(self):
        self.client.login(username='admin', password='12345678')

        url = reverse('videos-detail', kwargs={'pk': self.video5.pk})
        response = self.client.get(url, content_type='application/json')

        # Validate status code
        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)

    def test_retrieve_video_with_user_1(self):
        video2 = MediaSerializer(self.video2).data
        self.client.login(username='user1', password='12345678')

        url = reverse('videos-detail', kwargs={'pk': self.video2.pk})
        response = self.client.get(url, content_type='application/json')

        # Validate status code
        self.assertEqual(status.HTTP_200_OK, response.status_code)

        # Validate video
        self.assertEqual(video2, response.data)

    def test_retrieve_video_with_user_2(self):
        video4 = MediaSerializer(self.video4).data
        self.client.login(username='user2', password='12345678')

        url = reverse('videos-detail', kwargs={'pk': self.video4.pk})
        response = self.client.get(url, content_type='application/json')

        # Validate status code
        self.assertEqual(status.HTTP_200_OK, response.status_code)

        # Validate video
        self.assertEqual(video4, response.data)

    def test_retrieve_video_with_key(self):
        video2 = MediaSerializer(self.video2).data

        url1 = reverse('videos-detail', kwargs={'pk': self.video2.pk})
        url2 = reverse('videos-detail', kwargs={'pk': self.video5.pk})
        header = {'HTTP_AUTHORIZATION': self.key.api_key}
        response1 = self.client.get(url1, content_type='application/json', **header)
        response2 = self.client.get(url2, content_type='application/json', **header)

        # Validate status code
        self.assertEqual(status.HTTP_200_OK, response1.status_code)
        self.assertEqual(status.HTTP_404_NOT_FOUND, response2.status_code)

        # Validate video
        self.assertEqual(video2, response1.data)

    # </editor-fold>

    # <editor-fold desc="Put Video TESTS">
    def test_put_video_annon_user(self):
        data = {
            "name": "foo",
            "channel": self.chan1.pk,
            "tags": [
                self.tag2.name
            ]
        }

        url = reverse('videos-detail', kwargs={'pk': self.video1.pk})
        response = self.client.put(url, data=data, format='json')

        # Validate status code
        self.assertEqual(status.HTTP_401_UNAUTHORIZED, response.status_code)

    def test_put_video_with_multiple_channels(self):
        data = {
            "name": "foo",
            "channel": [
                self.chan1.pk,
                self.chan2.pk,
                self.chan3.pk
            ],
            "tags": [
                self.tag2.name
            ]
        }
        self.client.login(username='user1', password='12345678')

        url = reverse('videos-detail', kwargs={'pk': self.video2.pk})
        response = self.client.put(url, data=data, format='json')

        # Validate status code
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)

    def test_put_video_superuser_with_org_1(self):
        data = {
            "name": "foo",
            "channel": self.chan1.pk,
            "tags": [
                self.tag1.name
            ],
            "ads_vast_url": None,
            "enable_ads": True,
            "autoplay": 'c'
        }

        self.client.login(username='admin', password='12345678')

        url = reverse('videos-detail', kwargs={'pk': self.video1.pk})
        response = self.client.put(url, data=data, format='json')

        # Validate status code
        self.assertEqual(status.HTTP_200_OK, response.status_code)

        # Validate channels
        self.assertEqual(data['channel'], response.json()['channel'])

        # Validate tags
        self.assertIn(data['tags'][0], response.json()['tags'])

        # Validate other fields
        self.assertEqual(data['name'], response.json()['name'])
        self.assertEqual(data['ads_vast_url'], response.json()['ads_vast_url'])
        self.assertEqual(data['enable_ads'], response.json()['enable_ads'])
        self.assertEqual(data['autoplay'], response.json()['autoplay'])

    def test_put_video_superuser_with_user_from_different_org(self):
        data = {
            "name": "foo",
            "channel": self.chan4.pk,
            "tags": [
                self.tag2.name,
                self.tag3.name
            ]
        }

        self.client.login(username='admin', password='12345678')

        url = reverse('videos-detail', kwargs={'pk': self.video1.pk})
        response = self.client.put(url, data=data, format='json')

        # Validate status code
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)

    def test_put_video_with_user_1_org_1(self):
        data = {
            "name": "foo",
            "channel": self.chan1.pk,
            "tags": [
                self.tag1.name
            ],
            "ads_vast_url": None,
            "enable_ads": True
        }

        self.client.login(username='user1', password='12345678')

        url = reverse('videos-detail', kwargs={'pk': self.video2.pk})
        response = self.client.put(url, data=data, format='json')

        # Validate status code
        self.assertEqual(status.HTTP_200_OK, response.status_code)

        # Validate channels
        self.assertEqual(data['channel'], response.json()['channel'])

        # Validate tags
        self.assertIn(data['tags'][0], response.json()['tags'])

        # Validate other fields
        self.assertEqual(data['name'], response.json()['name'])
        self.assertEqual(data['ads_vast_url'], response.json()['ads_vast_url'])
        self.assertEqual(data['enable_ads'], response.json()['enable_ads'])

    def test_put_video_user_2_with_org_2(self):
        data = {
            "name": "foo",
            "channel": self.chan4.pk,
            "tags": [
                self.tag2.name,
                self.tag3.name
            ],
            "ads_vast_url": None,
            "enable_ads": True,
            "autoplay": 'n'
        }
        self.client.login(username='user2', password='12345678')

        url = reverse('videos-detail', kwargs={'pk': self.video4.pk})
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
        self.assertEqual(data['autoplay'], response.json()['autoplay'])

    def test_put_video_with_key(self):
        data = {
            "name": "foo",
            "channel": self.chan1.pk,
            "tags": [
                self.tag1.name
            ],
            "ads_vast_url": None,
            "enable_ads": True
        }

        url = reverse('videos-detail', kwargs={'pk': self.video2.pk})
        header = {'HTTP_AUTHORIZATION': self.key.api_key}
        response = self.client.put(url, data=data, format='json', **header)

        # Validate status code
        self.assertEqual(status.HTTP_200_OK, response.status_code)

        # Validate channels
        self.assertEqual(data['channel'], response.json()['channel'])

        # Validate tags
        self.assertIn(data['tags'][0], response.json()['tags'])

        # Validate other fields
        self.assertEqual(data['name'], response.json()['name'])
        self.assertEqual(data['ads_vast_url'], response.json()['ads_vast_url'])
        self.assertEqual(data['enable_ads'], response.json()['enable_ads'])

    def test_put_video_id(self):
        data = {
            "name": "foo",
            "content_type": "video/mp4",
            "video_id": "12345",
            "ads_vast_url": None,
            "enable_ads": False,
            "autoplay": 'c',
        }

        self.client.login(username='admin', password='12345678')

        creation_url = reverse('videos-list')
        creation_response = self.client.post(creation_url, data=data, format='json')

        # Validate status code
        self.assertEqual(status.HTTP_201_CREATED, creation_response.status_code)

        pk = creation_response.data['id']

        put_data = {
            "name": "updated_foo",
            "content_type": "video/mp4",
            "video_id": "123",
            "channel": self.chan2.pk,
            "tags": [
                self.tag1.name
            ],
            "ads_vast_url": "http://www.vast.com",
            "enable_ads": True,
            "autoplay": 'y'
        }

        url = reverse('videos-detail', kwargs={'pk': pk})
        response = self.client.put(url, data=put_data, format='json')

        # Validate status code
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Validate video fields
        self.assertEqual(put_data['name'], response.data['name'])
        self.assertEqual(put_data['autoplay'], response.data['autoplay'])
        self.assertEqual(put_data['enable_ads'], response.data['enable_ads'])
        self.assertEqual(put_data['ads_vast_url'], response.data['ads_vast_url'])

        # video_id is not editable so it should not change
        self.assertTrue('video_id' not in response.data)

        url = reverse('videos-detail', kwargs={'pk': creation_response.data['id']})
        response = self.client.get(url, format='json')

        # Validate video id
        self.assertEquals(data['video_id'], response.data['video_id'])

    # </editor-fold>

    # <editor-fold desc="Patch Video TESTS">
    def test_patch_video_with_annon_user(self):
        url = reverse('videos-detail', kwargs={'pk': self.video1.pk})
        response = self.client.patch(url, content_type='application/json')

        # Validate status code
        self.assertEqual(status.HTTP_401_UNAUTHORIZED, response.status_code)

    def test_patch_video_with_multiple_channels(self):
        data = {
            "name": "New name",
            "channel": [
                self.chan1.pk,
                self.chan3.pk
            ]
        }
        self.client.login(username='user1', password='12345678')

        url = reverse('videos-detail', kwargs={'pk': self.video1.pk})
        response = self.client.patch(url, data=data, format='json')

        # Validate status code
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)

    def test_patch_video_with_superuser(self):
        data = {
            "name": "New name",
            "channel": self.chan1.pk,
        }

        self.client.login(username='admin', password='12345678')

        url = reverse('videos-detail', kwargs={'pk': self.video1.pk})
        response = self.client.patch(url, data=data, format='json')

        # Validate status code
        self.assertEqual(status.HTTP_200_OK, response.status_code)

        # Validate video name
        self.assertEqual(data['name'], response.data["name"])

        # Validate video channels
        self.assertEqual(self.chan1.pk, response.json()['channel'])

    def test_patch_video_with_user_from_different_org(self):
        data = {
            "name": "New name",
            "channel": self.chan2.pk,
        }
        self.client.login(username='admin', password='12345678')

        url = reverse('videos-detail', kwargs={'pk': self.video4.pk})
        response = self.client.patch(url, data=data, format='json')

        # Validate status code
        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)

    def test_patch_video_with_user(self):
        create_data = {
            "name": "foo",
            "content_type": "video/mp4"
        }

        self.client.login(username='user2', password='12345678')

        url = reverse('videos-list')
        creation_response = self.client.post(url, data=create_data, format='json')

        # Validate status code
        self.assertEqual(status.HTTP_201_CREATED, creation_response.status_code)

        pk = creation_response.data['id']

        patch_data = {
            "name": "Lorem",
            "channel": self.chan4.pk,
        }

        url_patch = reverse('videos-detail', kwargs={'pk': pk})
        response = self.client.patch(url_patch, data=patch_data, format='json')

        # Validate status code
        self.assertEqual(status.HTTP_200_OK, response.status_code)

        # Validate video name
        self.assertEqual(response.data["name"], patch_data['name'])

        # Validate video channels
        self.assertEqual(self.chan4.pk, response.json()['channel'])

    def test_patch_video_with_key(self):
        create_data = {
            "name": "foo",
            "content_type": "video/mp4"
        }

        url = reverse('videos-list')
        header = {'HTTP_AUTHORIZATION': self.key.api_key}
        creation_response = self.client.post(url, data=create_data, format='json', **header)

        # Validate status code
        self.assertEqual(status.HTTP_201_CREATED, creation_response.status_code)

        pk = creation_response.data['id']

        patch_data = {
            "name": "Lorem",
            "channel": self.chan1.pk,
        }

        url_patch = reverse('videos-detail', kwargs={'pk': pk})
        url2 = reverse('videos-detail', kwargs={'pk': self.video4.pk})
        header = {'HTTP_AUTHORIZATION': self.key.api_key}
        response1 = self.client.patch(url_patch, data=patch_data, format='json', **header)
        response2 = self.client.patch(url2, data=patch_data, format='json', **header)

        # Validate status code
        self.assertEqual(status.HTTP_200_OK, response1.status_code)
        self.assertEqual(status.HTTP_404_NOT_FOUND, response2.status_code)

        # Validate video name
        self.assertEqual(response1.data["name"], patch_data['name'])

        # Validate video channels
        self.assertEqual(self.chan1.pk, response1.json()['channel'])

    def test_patch_video_without_channels(self):
        self.client.login(username='user2', password='12345678')

        create_data = {
            "name": "foo",
            "content_type": "video/mp4"
        }

        self.client.login(username='user2', password='12345678')

        url = reverse('videos-list')
        creation_response = self.client.post(url, data=create_data, format='json')

        # Validate status code
        self.assertEqual(status.HTTP_201_CREATED, creation_response.status_code)

        pk = creation_response.data['id']

        patch_data = {
            "name": "Lorem",
        }

        url_patch = reverse('videos-detail', kwargs={'pk': pk})
        response = self.client.patch(url_patch, data=patch_data, format='json')

        # Validate status code
        self.assertEqual(status.HTTP_200_OK, response.status_code)

        # Validate video name
        self.assertEqual(response.data["name"], patch_data['name'])

        # Validate video channels
        self.assertNotEqual(self.chan4.pk, response.json()['channel'])
        self.assertNotEqual(self.chan5.pk, response.json()['channel'])

    def test_patch_video_id(self):
        data = {
            "name": "foo",
            "content_type": "video/mp4",
            "video_id": "12345",
            "channel": self.chan1.pk
        }

        self.client.login(username='admin', password='12345678')

        creation_url = reverse('videos-list')
        creation_response = self.client.post(creation_url, data=data, format='json')

        # Validate status code
        self.assertEqual(status.HTTP_201_CREATED, creation_response.status_code)

        pk = creation_response.data['id']

        patch_data = {
            "name": "foo",
            "content_type": "video/mp4",
            "video_id": "1",
            "channel": self.chan1.pk,
        }

        url_patch = reverse('videos-detail', kwargs={'pk': pk})
        response = self.client.patch(url_patch, data=patch_data, format='json')

        # Validate status code
        self.assertEqual(status.HTTP_200_OK, response.status_code)

        # video_id is not editable so it should not change
        self.assertTrue('video_id' not in response.data)

        url = reverse('videos-detail', kwargs={'pk': creation_response.data['id']})
        response = self.client.get(url, format='json')

        # Validate video id
        self.assertEquals(data['video_id'], response.data['video_id'])

        def test_patch_video_user_2_with_disabled_org(self):
            self.client.login(username='user2', password='12345678')

            create_data = {
                "name": "foo",
                "content_type": "video/mp4"
            }

            self.client.login(username='user2', password='12345678')

            url = reverse('videos-list')
            creation_response = self.client.post(url, data=create_data, format='json')

            # Validate status code
            self.assertEqual(status.HTTP_201_CREATED, creation_response.status_code)

            pk = creation_response.data['id']

            self.org2.upload_enabled = False
            self.org2.save()

            patch_data = {
                "name": "Lorem",
            }

            url_patch = reverse('videos-detail', kwargs={'pk': pk})
            response = self.client.patch(url_patch, data=patch_data, format='json')

            # Validate status code
            self.assertEqual(status.HTTP_200_OK, response.status_code)

            # Validate video name
            self.assertEqual(response.data["name"], patch_data['name'])

            self.org2.upload_enabled = True
            self.org2.save()

    # </editor-fold>

    # <editor-fold desc="Create Video TESTS">
    def test_create_video_annon_user(self):
        data = {
            "name": "foo",
            "content_type": "video/mp4"
        }
        url = reverse('videos-list')
        response = self.client.post(url, data=data, format='json')

        # Validate status code
        self.assertEqual(status.HTTP_401_UNAUTHORIZED, response.status_code)

    def test_create_video_superuser_with_org_1(self):
        data = {
            "name": "foo",
            "content_type": "video/mp4"
        }

        self.client.login(username='admin', password='12345678')

        url = reverse('videos-list')
        response = self.client.post(url, data=data, format='json')

        # Validate status code
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)

    def test_create_video_user_1_with_org_1(self):
        data = {
            "name": "foo",
            "content_type": "video/mp4"
        }

        self.client.login(username='user1', password='12345678')

        url = reverse('videos-list')
        response = self.client.post(url, data=data, format='json')

        # Validate status code
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)

    def test_create_video_with_key(self):
        data = {
            "name": "foo",
            "content_type": "video/mp4"
        }

        url = reverse('videos-list')
        header = {'HTTP_AUTHORIZATION': self.key.api_key}
        response = self.client.post(url, data=data, format='json', **header)

        # Validate status code
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)

    def test_create_video_user_2_with_org_2(self):
        data = {
            "name": "foo",
            "content_type": "video/mp4"
        }

        self.client.login(username='user2', password='12345678')

        url = reverse('videos-list')
        response = self.client.post(url, data=data, format='json')

        # Validate status code
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)

    def test_create_video_with_different_content_type(self):
        data = {
            "name": "foo",
            "content_type": "other/content-type"
        }

        self.client.login(username='user2', password='12345678')

        url = reverse('videos-list')
        response = self.client.post(url, data=data, format='json')

        # Validate status code
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)

    def test_create_video_with_id(self):
        data = {
            "name": "foo",
            "content_type": "video/mp4",
            "video_id": '12345'
        }

        self.client.login(username='admin', password='12345678')

        url = reverse('videos-list')
        response = self.client.post(url, data=data, format='json')

        # Validate status code
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)

        # Validate video id
        self.assertEqual(data['video_id'], response.data['video_id'])

    def test_create_video_user_2_with_disabled_org(self):
        self.org2.upload_enabled = False
        self.org2.save()

        data = {
            "name": "foo",
            "content_type": "video/mp4"
        }

        self.client.login(username='user2', password='12345678')

        url = reverse('videos-list')
        response = self.client.post(url, data=data, format='json')

        # Validate status code
        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)

        self.org2.upload_enabled = True
        self.org2.save()

    # </editor-fold>

    # <editor-fold desc="Delete Video TESTS">
    def test_delete_video_with_annon_user(self):
        url = reverse('videos-detail', kwargs={'pk': self.video1.pk})
        response = self.client.delete(url, content_type='application/json')

        # Validate status code
        self.assertEqual(status.HTTP_401_UNAUTHORIZED, response.status_code)

    def test_delete_video_with_superuser(self):
        self.client.login(username='admin', password='12345678')

        url = reverse('videos-detail', kwargs={'pk': self.video1.pk})
        response = self.client.delete(url, content_type='application/json')

        # Validate status code
        self.assertEqual(status.HTTP_204_NO_CONTENT, response.status_code)

    def test_delete_video_with_user(self):
        self.client.login(username='user2', password='12345678')

        url = reverse('videos-detail', kwargs={'pk': self.video4.pk})
        response = self.client.delete(url, content_type='application/json')

        # Validate status code
        self.assertEqual(status.HTTP_204_NO_CONTENT, response.status_code)

    def test_delete_video_with_user_from_different_org(self):
        self.client.login(username='user1', password='12345678')

        url = reverse('videos-detail', kwargs={'pk': self.video4.pk})
        response = self.client.delete(url, content_type='application/json')

        # Validate status code
        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)

    def test_delete_video_with_key(self):
        url1 = reverse('videos-detail', kwargs={'pk': self.video1.pk})
        url2 = reverse('videos-detail', kwargs={'pk': self.video4.pk})
        header = {'HTTP_AUTHORIZATION': self.key.api_key}
        response1 = self.client.delete(url1, content_type='application/json', **header)
        response2 = self.client.delete(url2, content_type='application/json', **header)

        # Validate status code
        self.assertEqual(status.HTTP_204_NO_CONTENT, response1.status_code)
        self.assertEqual(status.HTTP_404_NOT_FOUND, response2.status_code)

    # </editor-fold>

    # <editor-fold desc="Transition Video TESTS">
    def test_change_video_status_from_waiting_file_to_queued_with_user_2_org_2(self):
        video_waiting = create_video('Video', self.user2, self.org2, 1, Media.State.WAITING_FILE)

        self.client.login(username='user2', password='12345678')

        url = reverse('videos-to-queued', kwargs={'pk': video_waiting.pk})
        with mock.patch('utils.mediaconvert.transcode', side_effect=None):
            response = self.client.post(url, data=None, format=None)

        # Validate status code
        self.assertEqual(status.HTTP_200_OK, response.status_code)

        video_waiting_updated = Media.objects.get(id=video_waiting.pk)

        # Validate video state
        self.assertEqual(Media.State.QUEUED, video_waiting_updated.state)

    def test_change_video_status_from_waiting_file_to_queuing_failed_with_user_2_org_2(self):
        video_waiting = create_video('Video', self.user2, self.org2, 1, Media.State.WAITING_FILE)

        self.client.login(username='user2', password='12345678')

        url = reverse('videos-to-queued-failed', kwargs={'pk': video_waiting.pk})
        response = self.client.post(url, data=None, format=None)

        video_waiting_updated = Media.objects.get(pk=video_waiting.pk)

        # Validate status code
        self.assertEqual(status.HTTP_200_OK, response.status_code)

        # Validate video state
        self.assertEqual(Media.State.QUEUING_FAILED, video_waiting_updated.state)

    def test_change_video_status_from_waiting_file_to_processing_with_user_2_org_2(self):
        video_waiting = create_video('Video', self.user2, self.org2, 1, Media.State.WAITING_FILE)

        self.client.login(username='user2', password='12345678')

        url = reverse('videos-to-processing', kwargs={'pk': video_waiting.pk})
        response = self.client.post(url, data=None, format=None)

        # Validate status code
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)

    def test_change_video_status_from_waiting_file_to_processing_failed_with_user_2_org_2(self):
        video_waiting = create_video('Video', self.user2, self.org2, 1, Media.State.WAITING_FILE)

        self.client.login(username='user2', password='12345678')

        url = reverse('videos-to-processing-failed', kwargs={'pk': video_waiting.pk})
        response = self.client.post(url, data=None, format=None)

        # Validate status code
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)

    def test_change_video_status_from_waiting_file_to_finished_with_user_2_org_2(self):
        video_waiting = create_video('Video', self.user2, self.org2, 1, Media.State.WAITING_FILE)

        self.client.login(username='user2', password='12345678')

        url = reverse('videos-to-finished', kwargs={'pk': video_waiting.pk})
        with mock.patch('utils.s3.get_size', return_value=0):
            response = self.client.post(url, data=None, format=None)

        # Validate status code
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)

    def test_change_video_status_from_queued_to_queuing_failed_with_user_2_org_2(self):
        video_queued = create_video('Video', self.user2, self.org2, 1, Media.State.QUEUED)

        self.client.login(username='user2', password='12345678')

        url = reverse('videos-to-queued-failed', kwargs={'pk': video_queued.pk})
        response = self.client.post(url, data=None, format=None)

        # Validate status code
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)

    def test_change_video_status_from_queued_to_queued_with_user_2_org_2(self):
        video_queued = create_video('Video', self.user2, self.org2, 1, Media.State.QUEUED)

        self.client.login(username='user2', password='12345678')

        url = reverse('videos-to-queued', kwargs={'pk': video_queued.pk})
        response = self.client.post(url, data=None, format=None)

        # Validate status code
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)

    def test_change_video_status_from_queued_to_processing_failed_with_user_2_org_2(self):
        video_queued = create_video('Video', self.user2, self.org2, 1, Media.State.QUEUED)

        self.client.login(username='user2', password='12345678')

        url = reverse('videos-to-processing-failed', kwargs={'pk': video_queued.pk})
        response = self.client.post(url, data=None, format=None)

        # Validate status code
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)

    def test_change_video_status_from_queued_to_processing_with_user_2_org_2(self):
        video_queued = create_video('Video', self.user2, self.org2, 1, Media.State.QUEUED)

        self.client.login(username='user2', password='12345678')

        url = reverse('videos-to-processing', kwargs={'pk': video_queued.pk})
        response = self.client.post(url, data=None, format=None)

        video_queued_updated = Media.objects.get(pk=video_queued.pk)

        # Validate status code
        self.assertEqual(status.HTTP_200_OK, response.status_code)

        # Validate video state
        self.assertEqual(Media.State.PROCESSING, video_queued_updated.state)

    def test_change_video_status_from_queued_to_finished_with_user_2_org_2(self):
        video_queued = create_video('Video', self.user2, self.org2, 1, Media.State.QUEUED)

        self.client.login(username='user2', password='12345678')

        url = reverse('videos-to-finished', kwargs={'pk': video_queued.pk})
        with mock.patch('utils.s3.get_size', return_value=0):
            response = self.client.post(url, data=None, format=None)

        video_queued_updated = Media.objects.get(pk=video_queued.pk)

        # Validate status code
        self.assertEqual(status.HTTP_200_OK, response.status_code)

        # Validate video state
        self.assertEqual(Media.State.FINISHED, video_queued_updated.state)

    def test_change_video_status_from_processing_to_queuing_failed_with_user_2_org_2(self):
        video_processing = create_video('Video', self.user2, self.org2, 1, Media.State.PROCESSING)

        self.client.login(username='user2', password='12345678')

        url = reverse('videos-to-queued-failed', kwargs={'pk': video_processing.pk})
        response = self.client.post(url, data=None, format=None)

        # Validate status code
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)

    def test_change_video_status_from_processing_to_queued_with_user_2_org_2(self):
        video_processing = create_video('Video', self.user2, self.org2, 1, Media.State.PROCESSING)

        self.client.login(username='user2', password='12345678')

        url = reverse('videos-to-queued', kwargs={'pk': video_processing.pk})
        response = self.client.post(url, data=None, format=None)

        # Validate status code
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)

    def test_change_video_status_from_processing_to_processing_failed_with_user_2_org_2(self):
        video_processing = create_video('Video', self.user2, self.org2, 1, Media.State.PROCESSING)

        self.client.login(username='user2', password='12345678')

        url = reverse('videos-to-processing-failed', kwargs={'pk': video_processing.pk})
        response = self.client.post(url, data=None, format=None)

        video_processing_updated = Media.objects.get(pk=video_processing.pk)

        # Validate status code
        self.assertEqual(status.HTTP_200_OK, response.status_code)

        self.assertEqual(Media.State.PROCESSING_FAILED, video_processing_updated.state)

    def test_change_video_status_from_processing_to_processing_with_user_2_org_2(self):
        video_processing = create_video('Video', self.user2, self.org2, 1, Media.State.PROCESSING)

        self.client.login(username='user2', password='12345678')

        url = reverse('videos-to-processing', kwargs={'pk': video_processing.pk})
        response = self.client.post(url, data=None, format=None)

        # Validate status code
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)

    def test_change_video_status_from_processing_to_finished_with_user_2_org_2(self):
        video_processing = create_video('Video', self.user2, self.org2, 1, Media.State.PROCESSING)

        self.client.login(username='user2', password='12345678')

        url = reverse('videos-to-finished', kwargs={'pk': video_processing.pk})
        with mock.patch('utils.s3.get_size', return_value=0):
            response = self.client.post(url, data=None, format=None)

        video_processing_updated = Media.objects.get(pk=video_processing.pk)

        # Validate status code
        self.assertEqual(status.HTTP_200_OK, response.status_code)

        self.assertEqual(Media.State.FINISHED, video_processing_updated.state)

    def test_change_video_status_from_finished_to_processing_failed_with_user_2_org_2(self):
        video_finished = create_video('Video', self.user2, self.org2, 1, Media.State.FINISHED)

        self.client.login(username='user2', password='12345678')

        url = reverse('videos-to-processing-failed', kwargs={'pk': video_finished.pk})
        response = self.client.post(url, data=None, format=None)

        # Validate status code
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)

    def test_change_video_status_from_finished_to_processing_with_user_2_org_2(self):
        video_finished = create_video('Video', self.user2, self.org2, 1, Media.State.FINISHED)

        self.client.login(username='user2', password='12345678')

        url = reverse('videos-to-processing', kwargs={'pk': video_finished.pk})
        response = self.client.post(url, data=None, format=None)

        # Validate status code
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)

    def test_change_video_status_from_finished_to_queuing_failed_with_user_2_org_2(self):
        video_finished = create_video('Video', self.user2, self.org2, 1, Media.State.FINISHED)

        self.client.login(username='user2', password='12345678')

        url = reverse('videos-to-queued-failed', kwargs={'pk': video_finished.pk})
        response = self.client.post(url, data=None, format=None)

        # Validate status code
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)

    def test_change_video_status_from_finished_to_queued_with_user_2_org_2(self):
        video_finished = create_video('Video', self.user2, self.org2, 1, Media.State.FINISHED)

        self.client.login(username='user2', password='12345678')

        url = reverse('videos-to-queued', kwargs={'pk': video_finished.pk})
        response = self.client.post(url, data=None, format=None)

        # Validate status code
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)
    # </editor-fold>
