import logging

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from api.serializers.tag import TagSerializer
from test_utils import (
    create_organizations,
    create_user,
    create_superuser,
    create_tags,
    create_key,
)
from video.models import Tag


class TagTests(APITestCase):
    @classmethod
    def setUpClass(cls):
        logging.disable(logging.WARNING)

        cls.org1, cls.org2 = create_organizations('Organization', 2)

        cls.user1 = create_user('user1', '12345678', cls.org1)
        cls.user2 = create_user('user2', '12345678', cls.org2)
        cls.su = create_superuser('admin', '12345678', cls.org1)
        cls.key = create_key('key', cls.user1)

    def setUp(self):
        self.tag1, self.tag2, self.tag3 = create_tags(
            'Funny tag', self.org1, 3
        )
        self.tag4, self.tag5, self.tag6 = create_tags(
            'Funny tag', self.org2, 3
        )

    def tearDown(self):
        Tag.objects.all().delete()

    @classmethod
    def tearDownClass(cls):
        logging.disable(logging.NOTSET)
        cls.org1.delete()
        cls.org2.delete()

    # <editor-fold desc="List Tag TESTS">
    def test_list_tags_with_annon_user(self):
        url = reverse('tags-list')
        response = self.client.get(url, format='json')

        # Validate status code
        self.assertEqual(status.HTTP_401_UNAUTHORIZED, response.status_code)

    def test_list_tags_with_superuser(self):
        tag1 = TagSerializer(self.tag1).data
        tag2 = TagSerializer(self.tag2).data
        tag3 = TagSerializer(self.tag3).data

        self.client.login(username='admin', password='12345678')

        url = reverse('tags-list')
        response = self.client.get(url, format='json')

        # Validate status code
        self.assertEqual(status.HTTP_200_OK, response.status_code)

        # Validate tags in results
        self.assertIn(tag1, response.json()['results'])
        self.assertIn(tag2, response.json()['results'])
        self.assertIn(tag3, response.json()['results'])

    def test_list_tags_with_user_1(self):
        tag1 = TagSerializer(self.tag1).data
        tag2 = TagSerializer(self.tag2).data
        tag3 = TagSerializer(self.tag3).data

        self.client.login(username='user1', password='12345678')

        url = reverse('tags-list')
        response = self.client.get(url, format='json')

        # Validate status code
        self.assertEqual(status.HTTP_200_OK, response.status_code)

        # Validate tags in results
        self.assertIn(tag1, response.json()['results'])
        self.assertIn(tag2, response.json()['results'])
        self.assertIn(tag3, response.json()['results'])

    def test_list_other_organization_tags_with_user_1(self):
        tag4 = TagSerializer(self.tag4).data
        tag5 = TagSerializer(self.tag5).data
        tag6 = TagSerializer(self.tag6).data

        self.client.login(username='user1', password='12345678')

        url = reverse('tags-list')
        response = self.client.get(url, format='json')

        # Validate status code
        self.assertEqual(status.HTTP_200_OK, response.status_code)

        # Validate tags in results
        self.assertNotIn(tag4, response.json()['results'])
        self.assertNotIn(tag5, response.json()['results'])
        self.assertNotIn(tag6, response.json()['results'])

    def test_list_tags_with_key(self):
        tag1 = TagSerializer(self.tag1).data
        tag2 = TagSerializer(self.tag2).data
        tag3 = TagSerializer(self.tag3).data
        tag4 = TagSerializer(self.tag4).data
        tag5 = TagSerializer(self.tag5).data
        tag6 = TagSerializer(self.tag6).data

        url = reverse('tags-list')
        header = {'HTTP_AUTHORIZATION': self.key.api_key}
        response = self.client.get(url, format='json', **header)

        # Validate status code
        self.assertEqual(status.HTTP_200_OK, response.status_code)

        # Validate tags in results
        self.assertIn(tag1, response.json()['results'])
        self.assertIn(tag2, response.json()['results'])
        self.assertIn(tag3, response.json()['results'])
        self.assertNotIn(tag4, response.json()['results'])
        self.assertNotIn(tag5, response.json()['results'])
        self.assertNotIn(tag6, response.json()['results'])

    # </editor-fold>

    # <editor-fold desc="Create Tag TESTS">
    def test_create_tag_annon_user(self):
        data = {"name": "foo"}

        url = reverse('tags-list')
        response = self.client.post(url, data=data, format='json')

        # Validate status code
        self.assertEqual(status.HTTP_401_UNAUTHORIZED, response.status_code)

    def test_create_tag_superuser(self):
        data = {"name": "foo"}

        self.client.login(username='admin', password='12345678')

        url = reverse('tags-list')
        response = self.client.post(url, data=data, format='json')

        # Validate status code
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)

    def test_create_tag_user_1(self):
        data = {"name": "foo"}

        self.client.login(username='user1', password='12345678')

        url = reverse('tags-list')
        response = self.client.post(url, data=data, format='json')

        # Validate status code
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)

    def test_create_tag_with_key(self):
        data = {"name": "foo"}

        url = reverse('tags-list')
        header = {'HTTP_AUTHORIZATION': self.key.api_key}
        response = self.client.post(url, data=data, format='json', **header)

        # Validate status code
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)

    def test_create_same_tags_different_organizations(self):
        data = {"name": "foo"}

        self.client.login(username='admin', password='12345678')

        url = reverse('tags-list')
        response = self.client.post(url, data=data, format='json')

        # Validate status code for org1
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)

        self.client.login(username=self.user2.username, password='12345678')

        url = reverse('tags-list')
        response = self.client.post(url, data=data, format='json')

        # Validate status code for org2
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)

    # </editor-fold>

    # <editor-fold desc="Put Tag TESTS">
    def test_put_tag_annon_user(self):
        data = {"name": "foo"}
        url = reverse('tags-detail', kwargs={'pk': self.tag1.pk})
        response = self.client.put(url, data=data, format='json')

        # Validate status code
        self.assertEqual(status.HTTP_401_UNAUTHORIZED, response.status_code)

    def test_put_tag_superuser(self):
        data = {"name": "foo"}
        self.client.login(username='admin', password='12345678')

        url = reverse('tags-detail', kwargs={'pk': self.tag1.pk})
        response = self.client.put(url, data=data, format='json')

        # Validate status code
        self.assertEqual(
            status.HTTP_405_METHOD_NOT_ALLOWED, response.status_code
        )

    def test_put_tag_user_1(self):
        data = {"name": "foo"}

        self.client.login(username='user1', password='12345678')

        url = reverse('tags-detail', kwargs={'pk': self.tag1.pk})
        response = self.client.put(url, data=data, format='json')

        # Validate status code
        self.assertEqual(
            status.HTTP_405_METHOD_NOT_ALLOWED, response.status_code
        )

    def test_put_tag_with_key(self):
        data = {"name": "foo"}

        url = reverse('tags-detail', kwargs={'pk': self.tag1.pk})
        header = {'HTTP_AUTHORIZATION': self.key.api_key}
        response = self.client.put(url, data=data, format='json', **header)

        # Validate status code
        self.assertEqual(
            status.HTTP_405_METHOD_NOT_ALLOWED, response.status_code
        )

    # </editor-fold>

    # <editor-fold desc="Patch Tag TESTS">
    def test_patch_tag_with_annon_user(self):
        url = reverse('tags-detail', kwargs={'pk': self.tag1.pk})
        response = self.client.patch(url, content_type='application/json')

        # Validate status code
        self.assertEqual(status.HTTP_401_UNAUTHORIZED, response.status_code)

    def test_patch_tag_with_superuser(self):
        self.client.login(username='admin', password='12345678')

        url = reverse('tags-detail', kwargs={'pk': self.tag1.pk})
        response = self.client.patch(url, content_type='application/json')

        # Validate status code
        self.assertEqual(
            status.HTTP_405_METHOD_NOT_ALLOWED, response.status_code
        )

    def test_patch_tag_with_user_1(self):
        self.client.login(username='user1', password='12345678')

        url = reverse('tags-detail', kwargs={'pk': self.tag4.pk})
        response = self.client.patch(url, content_type='application/json')

        # Validate status code
        self.assertEqual(
            status.HTTP_405_METHOD_NOT_ALLOWED, response.status_code
        )

    def test_patch_tag_with_key(self):
        url = reverse('tags-detail', kwargs={'pk': self.tag4.pk})
        header = {'HTTP_AUTHORIZATION': self.key.api_key}
        response = self.client.patch(
            url, content_type='application/json', **header
        )

        # Validate status code
        self.assertEqual(
            status.HTTP_405_METHOD_NOT_ALLOWED, response.status_code
        )

    # </editor-fold>

    # <editor-fold desc="Delete tag TESTS">
    def test_delete_tag_with_annon_user(self):
        url = reverse('tags-detail', kwargs={'pk': self.tag1.pk})
        response = self.client.delete(url, content_type='application/json')

        # Validate status code
        self.assertEqual(status.HTTP_401_UNAUTHORIZED, response.status_code)

    def test_delete_tag_with_superuser(self):
        self.client.login(username='admin', password='12345678')

        url = reverse('tags-detail', kwargs={'pk': self.tag1.pk})
        response = self.client.delete(url, content_type='application/json')

        # Validate status code
        self.assertEqual(status.HTTP_204_NO_CONTENT, response.status_code)

    def test_delete_tag_with_user_1(self):
        self.client.login(username='user1', password='12345678')

        url = reverse('tags-detail', kwargs={'pk': self.tag1.pk})
        response = self.client.delete(url, content_type='application/json')

        # Validate status code
        self.assertEqual(status.HTTP_204_NO_CONTENT, response.status_code)

    def test_delete_tag_with_user_from_different_org(self):
        self.client.login(username='user1', password='12345678')

        url = reverse('tags-detail', kwargs={'pk': self.tag4.pk})
        response = self.client.delete(url, content_type='application/json')

        # Validate status code
        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)

    def test_delete_tag_with_key(self):
        url1 = reverse('tags-detail', kwargs={'pk': self.tag1.pk})
        url2 = reverse('tags-detail', kwargs={'pk': self.tag4.pk})
        header = {'HTTP_AUTHORIZATION': self.key.api_key}
        response1 = self.client.delete(
            url1, content_type='application/json', **header
        )
        response2 = self.client.delete(
            url2, content_type='application/json', **header
        )

        # Validate status code
        self.assertEqual(status.HTTP_204_NO_CONTENT, response1.status_code)
        self.assertEqual(status.HTTP_404_NOT_FOUND, response2.status_code)

    # </editor-fold>
