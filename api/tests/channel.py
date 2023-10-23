import logging

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from api.serializers import ChannelSerializer
from organization.models import Channel
from test_utils import create_organizations, create_user, create_superuser, create_channels, \
    create_key


class ChannelTests(APITestCase):

    @classmethod
    def setUpClass(cls):
        logging.disable(logging.WARNING)

        cls.org1, cls.org2 = create_organizations('Organization', 2)

        cls.user1 = create_user('user1', '12345678', cls.org1)
        cls.user2 = create_user('user2', '12345678', cls.org2)
        cls.su = create_superuser('admin', '12345678', cls.org1)
        cls.key = create_key('key', cls.user1)

    def setUp(self):
        self.channel1, self.channel2, self.channel3 = create_channels('Channel', self.org1, 3)
        self.channel4, self.channel5 = create_channels('Channel', self.org2, 2)

    def tearDown(self):
        Channel.objects.all().delete()

    @classmethod
    def tearDownClass(cls):
        logging.disable(logging.NOTSET)
        cls.org1.delete()
        cls.org2.delete()

    # <editor-fold desc="List Channel TESTS">
    def test_list_channels_with_annon_user(self):
        url = reverse('channels-list')
        response = self.client.get(url, format='json')

        # Validate status code
        self.assertEqual(status.HTTP_401_UNAUTHORIZED, response.status_code)

    def test_list_channels_with_superuser(self):
        channel1 = ChannelSerializer(self.channel1).data
        channel2 = ChannelSerializer(self.channel2).data
        channel3 = ChannelSerializer(self.channel3).data
        channel4 = ChannelSerializer(self.channel4).data
        channel5 = ChannelSerializer(self.channel5).data

        self.client.login(username='admin', password='12345678')

        url = reverse('channels-list')
        response = self.client.get(url, format='json')

        # Validate status code
        self.assertEqual(status.HTTP_200_OK, response.status_code)

        # Validate channels in results
        self.assertIn(channel1, response.json()['results'])
        self.assertIn(channel2, response.json()['results'])
        self.assertIn(channel3, response.json()['results'])
        self.assertNotIn(channel4, response.json()['results'])
        self.assertNotIn(channel5, response.json()['results'])

    def test_list_channels_with_user_1(self):
        channel1 = ChannelSerializer(self.channel1).data
        channel2 = ChannelSerializer(self.channel2).data
        channel3 = ChannelSerializer(self.channel3).data
        channel4 = ChannelSerializer(self.channel4).data
        channel5 = ChannelSerializer(self.channel5).data

        self.client.login(username='user1', password='12345678')

        url = reverse('channels-list')
        response = self.client.get(url, format='json')

        # Validate status code
        self.assertEqual(status.HTTP_200_OK, response.status_code)

        # Validate channels in results
        self.assertIn(channel1, response.json()['results'])
        self.assertIn(channel2, response.json()['results'])
        self.assertIn(channel3, response.json()['results'])
        self.assertNotIn(channel4, response.json()['results'])
        self.assertNotIn(channel5, response.json()['results'])

    def test_list_channels_with_user_2(self):
        channel1 = ChannelSerializer(self.channel1).data
        channel2 = ChannelSerializer(self.channel2).data
        channel3 = ChannelSerializer(self.channel3).data
        channel4 = ChannelSerializer(self.channel4).data
        channel5 = ChannelSerializer(self.channel5).data

        self.client.login(username='user2', password='12345678')

        url = reverse('channels-list')
        response = self.client.get(url, format='json')

        # Validate status code
        self.assertEqual(status.HTTP_200_OK, response.status_code)

        # Validate channels in results
        self.assertNotIn(channel1, response.json()['results'])
        self.assertNotIn(channel2, response.json()['results'])
        self.assertNotIn(channel3, response.json()['results'])
        self.assertIn(channel4, response.json()['results'])
        self.assertIn(channel5, response.json()['results'])

    def test_list_channels_with_key(self):
        channel1 = ChannelSerializer(self.channel1).data
        channel2 = ChannelSerializer(self.channel2).data
        channel3 = ChannelSerializer(self.channel3).data
        channel4 = ChannelSerializer(self.channel4).data
        channel5 = ChannelSerializer(self.channel5).data

        url = reverse('channels-list')
        header = {'HTTP_AUTHORIZATION': self.key.api_key}
        response = self.client.get(url, format='json', **header)

        # Validate status code
        self.assertEqual(status.HTTP_200_OK, response.status_code)

        # Validate channels in results
        self.assertIn(channel1, response.json()['results'])
        self.assertIn(channel2, response.json()['results'])
        self.assertIn(channel3, response.json()['results'])
        self.assertNotIn(channel4, response.json()['results'])
        self.assertNotIn(channel5, response.json()['results'])

    # </editor-fold>

    # <editor-fold desc="Retrieve Channel TESTS">
    def test_retrieve_channels_with_annon_user(self):
        url = reverse('channels-detail', kwargs={'pk': self.channel1.pk})
        response = self.client.get(url, content_type='application/json')

        # Validate status code
        self.assertEqual(status.HTTP_401_UNAUTHORIZED, response.status_code)

    def test_retrieve_channels_with_superuser_with_org_1(self):
        channel1 = ChannelSerializer(self.channel1).data
        self.client.login(username='admin', password='12345678')

        url = reverse('channels-detail', kwargs={'pk': self.channel1.pk})
        response = self.client.get(url, content_type='application/json')

        # Validate status code
        self.assertEqual(status.HTTP_200_OK, response.status_code)

        # Validate channel
        self.assertEqual(channel1, response.data)

    def test_retrieve_channels_with_user_from_different_org(self):
        self.client.login(username='admin', password='12345678')

        url = reverse('channels-detail', kwargs={'pk': self.channel5.pk})
        response = self.client.get(url, content_type='application/json')

        # Validate status code
        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)

    def test_retrieve_channels_with_user_1(self):
        channel2 = ChannelSerializer(self.channel2).data
        self.client.login(username='user1', password='12345678')

        url = reverse('channels-detail', kwargs={'pk': self.channel2.pk})
        response = self.client.get(url, content_type='application/json')

        # Validate status code
        self.assertEqual(status.HTTP_200_OK, response.status_code)

        # Validate channel
        self.assertEqual(channel2, response.data)

    def test_retrieve_channels_with_user_2(self):
        channel4 = ChannelSerializer(self.channel4).data
        self.client.login(username='user2', password='12345678')

        url = reverse('channels-detail', kwargs={'pk': self.channel4.pk})
        response = self.client.get(url, content_type='application/json')

        # Validate status code
        self.assertEqual(status.HTTP_200_OK, response.status_code)

        # Validate channel
        self.assertEqual(channel4, response.data)

    def test_retrieve_channel_with_key(self):
        channel2 = ChannelSerializer(self.channel2).data
        url1 = reverse('channels-detail', kwargs={'pk': self.channel2.pk})
        url2 = reverse('channels-detail', kwargs={'pk': self.channel5.pk})

        header = {'HTTP_AUTHORIZATION': self.key.api_key}
        response1 = self.client.get(url1, format='json', **header)
        response2 = self.client.get(url2, format='json', **header)

        # Validate status code
        self.assertEqual(status.HTTP_200_OK, response1.status_code)
        self.assertEqual(status.HTTP_404_NOT_FOUND, response2.status_code)

        # Validate channel
        self.assertEqual(channel2, response1.data)

    # </editor-fold>

    # <editor-fold desc="Create Channel TESTS">
    def test_create_channels_with_annon_user(self):
        data = {
            "name": "New Channel",
            "allowed_domains": "one, two, three, four"
        }
        url = reverse('channels-list')
        response = self.client.post(url, data=data, format='json')

        # Validate status code
        self.assertEqual(status.HTTP_401_UNAUTHORIZED, response.status_code)

    def test_create_channels_with_superuser(self):
        data = {
            "name": "New Channel",
            "allowed_domains": ["one", "two", "three", "four"]
        }

        self.client.login(username='admin', password='12345678')

        url = reverse('channels-list')
        response = self.client.post(url, data=data, format='json')

        # Validate status code
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)

    def test_create_channels_with_user_1(self):
        data = {
            "name": "New Channel",
            "allowed_domains": ["one", "two", "three", "four"]
        }

        self.client.login(username='user1', password='12345678')

        url = reverse('channels-list')
        response = self.client.post(url, data=data, format='json')

        # Validate status code
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)

    def test_create_channels_with_user_2(self):
        data = {
            "name": "New Channel",
            "allowed_domains": ["one", "two", "three", "four"]
        }

        self.client.login(username='user2', password='12345678')

        url = reverse('channels-list')
        response = self.client.post(url, data=data, format='json')

        # Validate status code
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)

    def test_create_channels_with_key(self):
        data = {
            "name": "New Channel",
            "allowed_domains": ["one", "two", "three", "four"]
        }

        url = reverse('channels-list')
        header = {'HTTP_AUTHORIZATION': self.key.api_key}
        response = self.client.post(url, data=data, format='json', **header)

        # Validate status code
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)

    # </editor-fold>

    # <editor-fold desc="Put Channel TESTS">
    def test_put_channel_annon_user(self):
        data = {
            "name": "New Channel",
            "allowed_domains": ["one", "two", "three", "four"]
        }
        url = reverse('channels-detail', kwargs={'pk': self.channel1.pk})
        response = self.client.put(url, data=data, format='json')

        # Validate status code
        self.assertEqual(status.HTTP_401_UNAUTHORIZED, response.status_code)

    def test_put_channel_superuser_with_org_1(self):
        data = {
            "name": "New Channel",
            "allowed_domains": ["one", "two", "three", "four"],
            "ads_vast_url": "",
            "detect_adblock": False,
            "autoplay": False
        }

        self.client.login(username='admin', password='12345678')

        url = reverse('channels-detail', kwargs={'pk': self.channel1.pk})
        response = self.client.put(url, data=data, format='json')

        # Validate status code
        self.assertEqual(status.HTTP_200_OK, response.status_code)

        # Validate allowed domains
        self.assertIn(data['allowed_domains'][0], response.json()['allowed_domains'])
        self.assertIn(data['allowed_domains'][1], response.json()['allowed_domains'])
        self.assertIn(data['allowed_domains'][2], response.json()['allowed_domains'])
        self.assertIn(data['allowed_domains'][3], response.json()['allowed_domains'])

        # Validate other fields
        self.assertEqual(data['name'], response.json()['name'])
        self.assertEqual(data['ads_vast_url'], response.json()['ads_vast_url'])
        self.assertEqual(data['detect_adblock'], response.json()['detect_adblock'])

    def test_put_channel_superuser_with_org_1_but_channels_org_2(self):
        data = {
            "name": "New Channel",
            "allowed_domains": ["one", "two", "three", "four"],
            "ads_vast_url": ""
        }

        self.client.login(username='admin', password='12345678')

        url = reverse('channels-detail', kwargs={'pk': self.channel4.pk})
        response = self.client.put(url, data=data, format='json')

        # Validate status code
        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)

    def test_put_channel_user_1_with_org_1(self):
        data = {
            "name": "New Channel",
            "allowed_domains": ["one", "two", "three", "four"],
            "ads_vast_url": "",
            "detect_adblock": False
        }

        self.client.login(username='user1', password='12345678')

        url = reverse('channels-detail', kwargs={'pk': self.channel3.pk})
        response = self.client.put(url, data=data, format='json')

        # Validate status code
        self.assertEqual(status.HTTP_200_OK, response.status_code)

        # Validate allowed domains
        self.assertIn(data['allowed_domains'][0], response.json()['allowed_domains'])
        self.assertIn(data['allowed_domains'][1], response.json()['allowed_domains'])
        self.assertIn(data['allowed_domains'][2], response.json()['allowed_domains'])
        self.assertIn(data['allowed_domains'][3], response.json()['allowed_domains'])

        # Validate other fields
        self.assertEqual(data['name'], response.json()['name'])
        self.assertEqual(data['ads_vast_url'], response.json()['ads_vast_url'])
        self.assertEqual(data['detect_adblock'], response.json()['detect_adblock'])

    def test_put_channel_user_2_with_org_2(self):
        data = {
            "name": "New Channel",
            "allowed_domains": ["one", "two", "three", "four"],
            "ads_vast_url": "",
            "detect_adblock": False,
            "autoplay": True
        }

        self.client.login(username='user2', password='12345678')

        url = reverse('channels-detail', kwargs={'pk': self.channel4.pk})
        response = self.client.put(url, data=data, format='json')

        # Validate status code
        self.assertEqual(status.HTTP_200_OK, response.status_code)

        # Validate allowed domains
        self.assertIn(data['allowed_domains'][0], response.json()['allowed_domains'])
        self.assertIn(data['allowed_domains'][1], response.json()['allowed_domains'])
        self.assertIn(data['allowed_domains'][2], response.json()['allowed_domains'])
        self.assertIn(data['allowed_domains'][3], response.json()['allowed_domains'])

        # Validate other fields
        self.assertEqual(data['name'], response.json()['name'])
        self.assertEqual(data['ads_vast_url'], response.json()['ads_vast_url'])
        self.assertEqual(data['detect_adblock'], response.json()['detect_adblock'])

    def test_put_channel_with_key(self):
        data = {
            "name": "New Channel",
            "allowed_domains": ["one", "two", "three", "four"],
            "ads_vast_url": "",
            "detect_adblock": False
        }

        url1 = reverse('channels-detail', kwargs={'pk': self.channel3.pk})
        url2 = reverse('channels-detail', kwargs={'pk': self.channel4.pk})

        header = {'HTTP_AUTHORIZATION': self.key.api_key}
        response1 = self.client.put(url1, data=data, format='json', **header)
        response2 = self.client.put(url2, data=data, format='json', **header)

        # Validate status code
        self.assertEqual(status.HTTP_200_OK, response1.status_code)
        self.assertEqual(status.HTTP_404_NOT_FOUND, response2.status_code)

        # Validate allowed domains
        self.assertIn(data['allowed_domains'][0], response1.json()['allowed_domains'])
        self.assertIn(data['allowed_domains'][1], response1.json()['allowed_domains'])
        self.assertIn(data['allowed_domains'][2], response1.json()['allowed_domains'])
        self.assertIn(data['allowed_domains'][3], response1.json()['allowed_domains'])

        # Validate other fields
        self.assertEqual(data['name'], response1.json()['name'])
        self.assertEqual(data['ads_vast_url'], response1.json()['ads_vast_url'])
        self.assertEqual(data['detect_adblock'], response1.json()['detect_adblock'])

    # </editor-fold>

    # <editor-fold desc="Patch Channel TESTS">
    def test_patch_channel_with_annon_user(self):
        url = reverse('channels-detail', kwargs={'pk': self.channel1.pk})
        response = self.client.patch(url, content_type='application/json')

        # Validate status code
        self.assertEqual(status.HTTP_401_UNAUTHORIZED, response.status_code)

    def test_patch_channel_with_superuser(self):
        create_data = {
            "name": "New Channel",
            "allowed_domains": ["one", "two", "three", "four"],
            "ads_vast_url": ""
        }

        self.client.login(username='admin', password='12345678')

        url = reverse('channels-list')
        creation_response = self.client.post(url, data=create_data, format='json')
        pk = creation_response.data["id"]

        patch_data = {
            "name": "Foo",
            "allowed_domains": ["111", "222"],
            "ads_vast_url": "https://www.dummy.com",
            "detect_adblock": True
        }

        url_patch = reverse('channels-detail', kwargs={'pk': pk})
        response = self.client.patch(url_patch, data=patch_data, format='json')

        # Validate status code
        self.assertEqual(status.HTTP_200_OK, response.status_code)

        # Validate name
        self.assertEqual(patch_data['name'], response.data["name"])

        # Validate allowed domains
        self.assertIn(patch_data['allowed_domains'][0], response.json()['allowed_domains'])
        self.assertIn(patch_data['allowed_domains'][1], response.json()['allowed_domains'])
        self.assertNotIn("333", response.json()['allowed_domains'])

        # Validate other fields
        self.assertEqual(patch_data['ads_vast_url'], response.json()['ads_vast_url'])
        self.assertEqual(patch_data['detect_adblock'], response.json()['detect_adblock'])

    def test_patch_channel_with_user(self):
        create_data = {
            "name": "New Channel",
            "allowed_domains": ["one", "two", "three", "four"],
            "ads_vast_url": ""
        }

        self.client.login(username='user2', password='12345678')

        url = reverse('channels-list')
        creation_response = self.client.post(url, data=create_data, format='json')
        pk = creation_response.data["id"]

        patch_data = {
            "name": "Lorem",
            "allowed_domains": ["one", "two"],
            "ads_vast_url": "https://www.lorem.com",
            "detect_adblock": True
        }

        url_patch = reverse('channels-detail', kwargs={'pk': pk})
        response = self.client.patch(url_patch, data=patch_data, format='json')

        # Validate status code
        self.assertEqual(status.HTTP_200_OK, response.status_code)

        # Validate name
        self.assertEqual(patch_data['name'], response.data["name"])

        # Validate allowed domains
        self.assertIn(patch_data['allowed_domains'][0], response.json()['allowed_domains'])
        self.assertIn(patch_data['allowed_domains'][1], response.json()['allowed_domains'])
        self.assertNotIn("three", response.json()['allowed_domains'])
        self.assertNotIn("four", response.json()['allowed_domains'])

        # Validate other fields
        self.assertEqual("https://www.lorem.com", response.json()['ads_vast_url'])
        self.assertEqual(patch_data['detect_adblock'], response.json()['detect_adblock'])

    def test_patch_channel_with_key(self):
        create_data = {
            "name": "New Channel",
            "allowed_domains": ["one", "two", "three", "four"],
            "ads_vast_url": ""
        }

        url = reverse('channels-list')
        header = {'HTTP_AUTHORIZATION': self.key.api_key}
        creation_response = self.client.post(url, data=create_data, format='json', **header)
        pk = creation_response.data["id"]

        patch_data = {
            "name": "Lorem",
            "allowed_domains": ["one", "two"],
            "ads_vast_url": "https://www.lorem.com",
            "detect_adblock": True
        }

        url_patch = reverse('channels-detail', kwargs={'pk': pk})
        response = self.client.patch(url_patch, data=patch_data, format='json', **header)

        # Validate status code
        self.assertEqual(status.HTTP_200_OK, response.status_code)

        # Validate name
        self.assertEqual(patch_data['name'], response.data["name"])

        # Validate allowed domains
        self.assertIn(patch_data['allowed_domains'][0], response.json()['allowed_domains'])
        self.assertIn(patch_data['allowed_domains'][1], response.json()['allowed_domains'])
        self.assertNotIn("three", response.json()['allowed_domains'])
        self.assertNotIn("four", response.json()['allowed_domains'])

        # Validate other fields
        self.assertEqual("https://www.lorem.com", response.json()['ads_vast_url'])
        self.assertEqual(patch_data['detect_adblock'], response.json()['detect_adblock'])
    # </editor-fold>
