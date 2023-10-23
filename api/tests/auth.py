import logging

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from api.serializers import AccountSerializer
from hub_auth.models import Account
from test_utils import create_organizations, create_user, create_superuser, create_key


class AccountTests(APITestCase):
    def setUp(self):
        logging.disable(logging.WARNING)

        # Organizations
        self.testOrg = create_organizations('Test Organization', 1)[0]

        # Accounts
        self.accountEP = create_user('accountEP', '12345678', self.testOrg)

        # Superuser
        self.su = create_superuser('super', '12345678', self.testOrg)

        # Key
        self.key = create_key('key', self.accountEP)

    def tearDown(self):
        logging.disable(logging.NOTSET)
        self.testOrg.delete()

    # <editor-fold desc="Annon user TESTS">
    def test_change_password_annon_user(self):
        data = {
            'old_password': '12345678',
            'new_password': '11111111',
            'new_password_2': '11111111'
        }

        url = reverse('accounts-change-password')
        response = self.client.post(url, data=data, format='json')

        # Validate status code
        self.assertEqual(status.HTTP_401_UNAUTHORIZED, response.status_code)

    def test_account_me_annon_user(self):
        url = reverse('accounts-me')
        response = self.client.get(url, format='json')

        # Validate status code
        self.assertEqual(status.HTTP_401_UNAUTHORIZED, response.status_code)

    def test_list_users_with_annon_user(self):
        url = reverse('accounts-list')
        response = self.client.get(url, format='json')

        # Validate status code
        self.assertEqual(status.HTTP_401_UNAUTHORIZED, response.status_code)

    def test_retrieve_user_with_annon_user(self):
        url = reverse('accounts-detail', kwargs={'pk': self.accountEP.pk})
        response = self.client.get(url, format='json')

        # Validate status code
        self.assertEqual(status.HTTP_401_UNAUTHORIZED, response.status_code)
    # </editor-fold>

    # <editor-fold desc="Registered User TESTS">
    def test_change_password_registered_account(self):
        self.client.login(username='accountEP', password='12345678')

        data = {
            'old_password': '12345678',
            'new_password': '11111111',
            'new_password_2': '11111111'
        }

        url = reverse('accounts-change-password')
        response = self.client.post(url, data=data, format='json')

        # Validate status code
        self.assertEqual(status.HTTP_200_OK, response.status_code)

        updated = Account.objects.get(username='accountEP')

        # Validate new password
        self.assertTrue(updated.check_password('11111111'))

    def test_change_password_registered_account_wrong_password(self):
        self.client.login(username='accountEP', password='12345678')

        data = {
            'old_password': '123',
            'new_password': '11111111',
            'new_password_2': '11111111'
        }

        url = reverse('accounts-change-password')
        response = self.client.post(url, data=data, format='json')

        # Validate status code
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)

        updated = Account.objects.get(username='accountEP')

        # Validate new password
        self.assertTrue(updated.check_password('12345678'))

    def test_change_password_registered_account_invalid_new_password(self):
        self.client.login(username='accountEP', password='12345678')

        data = {
            'old_password': '12345678',
            'new_password': '123',
            'new_password_2': '465'
        }

        url = reverse('accounts-change-password')
        response = self.client.post(url, data=data, format='json')

        # Validate status code
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)

        updated = Account.objects.get(username='accountEP')

        # Validate new password
        self.assertTrue(updated.check_password('12345678'))

    def test_account_me_registered_user(self):
        self.client.login(username='accountEP', password='12345678')

        url = reverse('accounts-me')
        response = self.client.get(url, format='json')

        # Validate status code
        self.assertEqual(status.HTTP_200_OK, response.status_code)

        account = AccountSerializer(self.accountEP).data

        # Validate account
        self.assertEqual(account, response.json())

    def test_list_users_with_registered_user(self):
        self.client.login(username='accountEP', password='12345678')

        url = reverse('accounts-list')
        response = self.client.get(url, format='json')

        # Validate status code
        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)

    def test_retrieve_user_with_registered_user(self):
        self.client.login(username='accountEP', password='12345678')

        url = reverse('accounts-detail', kwargs={'pk': self.accountEP.pk})
        response = self.client.get(url, format='json')

        # Validate status code
        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)
    # </editor-fold>

    # <editor-fold desc="Superuser TESTS">
    def test_change_password_with_superuser(self):
        self.client.login(username='super', password='12345678')

        data = {
            'old_password': '12345678',
            'new_password': '11111111',
            'new_password_2': '11111111'
        }

        url = reverse('accounts-change-password')
        response = self.client.post(url, data=data, format='json')

        # Validate status code
        self.assertEqual(status.HTTP_200_OK, response.status_code)

        updated = Account.objects.get(username='super')

        # Validate new password
        self.assertTrue(updated.check_password('11111111'))

    def test_account_me_with_superuser(self):
        self.client.login(username='super', password='12345678')

        url = reverse('accounts-me')
        response = self.client.get(url, format='json')

        # Validate status code
        self.assertEqual(status.HTTP_200_OK, response.status_code)

        account = AccountSerializer(self.su).data

        # Validate account
        self.assertEqual(account, response.json())

    def test_list_users_with_superuser(self):
        self.client.login(username='super', password='12345678')

        account1 = AccountSerializer(self.accountEP).data
        account2 = AccountSerializer(self.su).data

        url = reverse('accounts-list')
        response = self.client.get(url, format='json')

        # Validate status code
        self.assertEqual(status.HTTP_200_OK, response.status_code)

        # Validate account in results
        self.assertIn(account1, response.json()['results'])
        self.assertIn(account2, response.json()['results'])

    def test_retrieve_user_with_superuser(self):
        self.client.login(username='super', password='12345678')

        account = AccountSerializer(self.accountEP).data

        url = reverse('accounts-detail', kwargs={'pk': self.accountEP.pk})
        response = self.client.get(url, format='json')

        # Validate status code
        self.assertEqual(status.HTTP_200_OK, response.status_code)

        # Validate account in results
        self.assertEqual(account, response.json())
    # </editor-fold>

    # <editor-fold desc="Key TESTS">
    def test_change_password_key(self):
        data = {
            'old_password': '12345678',
            'new_password': '11111111',
            'new_password_2': '11111111'
        }

        url = reverse('accounts-change-password')
        header = {'HTTP_AUTHORIZATION': self.key.api_key}
        response = self.client.post(url, data=data, format='json', **header)

        # Validate status code
        self.assertEqual(status.HTTP_200_OK, response.status_code)

        updated = Account.objects.get(username='accountEP')

        # Validate new password
        self.assertTrue(updated.check_password('11111111'))

    def test_change_password_key_wrong_password(self):
        data = {
            'old_password': '123',
            'new_password': '11111111',
            'new_password_2': '11111111'
        }

        url = reverse('accounts-change-password')
        header = {'HTTP_AUTHORIZATION': self.key.api_key}
        response = self.client.post(url, data=data, format='json', **header)

        # Validate status code
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)

        updated = Account.objects.get(username='accountEP')

        # Validate new password
        self.assertTrue(updated.check_password('12345678'))

    def test_change_password_key_invalid_new_password(self):
        self.client.login(username='accountEP', password='12345678')

        data = {
            'old_password': '12345678',
            'new_password': '123',
            'new_password_2': '465'
        }

        url = reverse('accounts-change-password')
        header = {'HTTP_AUTHORIZATION': self.key.api_key}
        response = self.client.post(url, data=data, format='json', **header)

        # Validate status code
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)

        updated = Account.objects.get(username='accountEP')

        # Validate new password
        self.assertTrue(updated.check_password('12345678'))

    def test_account_me_key(self):
        url = reverse('accounts-me')
        header = {'HTTP_AUTHORIZATION': self.key.api_key}
        response = self.client.get(url, format='json', **header)

        # Validate status code
        self.assertEqual(status.HTTP_200_OK, response.status_code)

        account = AccountSerializer(self.accountEP).data

        # Validate account
        self.assertEqual(account, response.json())

    def test_list_users_with_key(self):
        url = reverse('accounts-list')
        header = {'HTTP_AUTHORIZATION': self.key.api_key}
        response = self.client.get(url, format='json', **header)

        # Validate status code
        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)

    def test_retrieve_user_with_key(self):
        url = reverse('accounts-detail', kwargs={'pk': self.accountEP.pk})
        header = {'HTTP_AUTHORIZATION': self.key.api_key}
        response = self.client.get(url, format='json', **header)

        # Validate status code
        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)
    # </editor-fold>
