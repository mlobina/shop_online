from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient, APITestCase
from rest_framework import status
from core.models import Contact
from rest_framework.utils import json
from user.serializers import ContactSerializer

CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')
ME_URL = reverse('user:me')


def create_user(**params):
    return get_user_model().objects.create_user(**params)


def create_contact(user, **params):
    defaults = {'city': 'testcity',
                'street': 'teststreet',
                'house': 'testhouse',
                'structure': 'teststructure',
                'building': 'testbuilding',
                'apartment': 'testapartment',
                'phone': 'testphone'}
    defaults.update(params)
    return Contact.objects.create(user=user, **defaults)


class PublicUserApiTests(TestCase):
    """Test the users API (public, without authentication)"""

    def setUp(self):
        self.client = APIClient()

    def test_create_valid_user_success(self):
        """Test creating using with a valid payload is successful"""
        payload = {
            'email': 'test@mail.com',
            'password': 'testpass',
            'name': 'name',
            'company': 'testcompany',
            'position': 'testposition'
        }
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(**res.data)
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password', res.data)

    def test_user_exists(self):
        """Test creating a user that already exists fails"""
        payload = {'email': 'test@mail.com', 'password': 'testpass', 'name': 'Test'}
        create_user(**payload)

        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short(self):
        """Test that the password must be more than 5 characters"""
        payload = {'email': 'test@mail.com', 'password': 'pw', 'name': 'Test'}
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        user_exists = get_user_model().objects.filter(
            email=payload['email']
        ).exists()
        self.assertFalse(user_exists)

    def test_create_token_for_user(self):
        """Test that a token is created for the user"""
        payload = {'email': 'test@mail.com', 'password': 'testpass'}
        create_user(**payload)
        res = self.client.post(TOKEN_URL, payload)

        self.assertIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_token_invalid_credentials(self):
        """Test that token is not created if invalid credentials are given"""
        create_user(email='test@mail.com', password='testpass')
        payload = {'email': 'test@mail.com', 'password': 'wrong'}
        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_no_user(self):
        """Test that token is not created if user does not exist"""
        payload = {'email': 'test@mail.com', 'password': 'testpass'}
        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_missing_field(self):
        """Test that email and password are required"""
        res = self.client.post(TOKEN_URL, {'email': 'one', 'password': ''})
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_user_unauthorized(self):
        """Test that authentication is required for users"""
        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateUserApiTests(TestCase):
    """Test API requests that require authentication"""

    def setUp(self):
        self.user = create_user(
            email='test@mail.com',
            password='testpass',
            name='Test',
            company='testcompany',
            position='testposition',
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retrieve_profile_success(self):
        """Test retrieving profile for logged in user"""
        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, {
            'id': self.user.id,
            'name': self.user.name,
            'email': self.user.email,
            'company': self.user.company,
            'position': self.user.position,
        })

    def test_post_me_not_allowed(self):
        """Test that POST is not allowed on the me URL"""
        res = self.client.post(ME_URL, {})

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_user_profile(self):
        """Test updating the user profile for authenticated user"""
        payload = {'name': 'new name', 'password': 'newtestpass'}

        res = self.client.patch(ME_URL, payload)

        self.user.refresh_from_db()
        self.assertEqual(self.user.name, payload['name'])
        self.assertTrue(self.user.check_password(payload['password']))
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_delete_user_profile(self):
        """Test deleting the user profile for authenticated user"""
        res = self.client.delete(ME_URL, {})

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)


class PublicContactApiTests(TestCase):
    """Test unauthenticated contact API access"""

    def setUp(self):
        self.client = APIClient()

    def test_required_auth(self):
        """Test the authenticaiton is required"""
        url = reverse('user:contact-list')
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateContactApiTests(TestCase):
    """Test authenticated contact API access"""

    def setUp(self):
        self.client = APIClient()
        self.user = create_user(
            email='user@mail.com',
            password='testpass',
            name='User',
            company='testcompany',
            position='testposition')

        self.staff = create_user(
            email='staff@mail.com',
            password='testpass',
            name='Staff',
            company='testcompany',
            position='testposition',
            is_staff=True)

    def test_data_serialized_successfully(self):
        contact_1 = create_contact(user=self.user)
        contact_2 = create_contact(user=self.staff)
        data = ContactSerializer([contact_1, contact_2], many=True).data
        expected_data = [
            {'id': contact_1.id,
             'city': 'testcity',
             'street': 'teststreet',
             'house': 'testhouse',
             'structure': 'teststructure',
             'building': 'testbuilding',
             'apartment': 'testapartment',
             'user': contact_1.user.id,
             'phone': 'testphone'
             },
            {'id': contact_2.id,
             'city': 'testcity',
             'street': 'teststreet',
             'house': 'testhouse',
             'structure': 'teststructure',
             'building': 'testbuilding',
             'apartment': 'testapartment',
             'user': contact_2.user.id,
             'phone': 'testphone'
             }
        ]

        self.assertEqual(expected_data, data)

    def test_list_by_staff(self):
        """Test staff getting a list of all contacts"""
        contact_1 = create_contact(user=self.user)
        contact_2 = create_contact(user=self.staff)
        url = reverse('user:contact-list')
        self.client.force_authenticate(user=self.staff)
        res = self.client.get(url)
        serializer_data = ContactSerializer([contact_1, contact_2], many=True).data

        self.assertEqual(status.HTTP_200_OK, res.status_code)
        self.assertEqual(serializer_data, res.data)
        self.assertEqual({serializer_data[0]['user'], serializer_data[1]['user']}, {res.data[0]['user'],
                                                                                    res.data[1]['user']})

    def test_list_by_user(self):
        """Test user getting a list of user's contacts"""
        contact_1 = create_contact(user=self.user)
        contact_2 = create_contact(user=self.staff)
        contact_3 = create_contact(user=self.user)
        url = reverse('user:contact-list')
        self.client.force_authenticate(user=self.user)
        res = self.client.get(url)
        serializer_data = ContactSerializer([contact_1, contact_3], many=True).data
        self.assertEqual(status.HTTP_200_OK, res.status_code)
        self.assertEqual({serializer_data[0]['user'], serializer_data[1]['user']}, {res.data[0]['user'],
                                                                                    res.data[1]['user']})

    def test_create(self):
        """Test creating a new contact"""
        url = reverse('user:contact-list')
        self.client.force_authenticate(user=self.user)
        data = {'city': 'testcity',
                'street': 'teststreet',
                'house': 'testhouse',
                'structure': 'teststructure',
                'building': 'testbuilding',
                'apartment': 'testapartment',
                'user': self.user.id,
                'phone': 'testphone'}
        json_data = json.dumps(data)
        res = self.client.post(url, data=json_data, content_type='application/json')

        self.assertEqual(status.HTTP_201_CREATED, res.status_code)
        self.assertEqual(data['phone'], res.data['phone'])

    def test_create_another_way(self):
        """Test creating a new contact"""
        url = reverse('user:contact-list')
        self.client.force_authenticate(user=self.user)
        payload = {'city': 'testcity',
                    'street': 'teststreet',
                    'house': 'testhouse',
                    'structure': 'teststructure',
                    'building': 'testbuilding',
                    'apartment': 'testapartment',
                    'user': self.user.id,
                    'phone': 'testphone'}
        res = self.client.post(url, payload)
        self.assertEqual(status.HTTP_201_CREATED, res.status_code)
        contact = Contact.objects.get(id=res.data['id'])
        self.assertEqual(payload['phone'], contact.phone)
        self.assertEqual(self.user, Contact.objects.last().user)

    def test_update_by_owner(self):
        """Test updating a contact by it's owner"""
        self.client.force_authenticate(user=self.user)
        new_contact = create_contact(user=self.user)
        url = reverse('user:contact-detail', args=[new_contact.id])
        data = {'street': 'updatestreet'}
        res = self.client.patch(url, data)

        self.assertEqual(status.HTTP_200_OK, res.status_code)
        self.assertNotEqual(new_contact.street, res.data['street'])

    def test_update_only_your_contact(self):
        """Test updating a contact only by it's owner"""
        self.client.force_authenticate(user=self.user)
        contact_1 = create_contact(user=self.user)
        contact_2 = create_contact(user=self.staff)
        url = reverse('user:contact-detail', args=[contact_2.id])
        url_own = reverse('user:contact-detail', args=[contact_1.id])
        data = {'house': 'updatehouse'}
        res = self.client.patch(url, data)
        res_own = self.client.patch(url_own, data)

        self.assertEqual(status.HTTP_404_NOT_FOUND, res.status_code)
        self.assertEqual(status.HTTP_200_OK, res_own.status_code)

    def test_update_any_contact_by_staff(self):
        """Test updating any contact by staff"""
        self.client.force_authenticate(user=self.staff)
        contact = create_contact(user=self.user)
        url = reverse('user:contact-detail', args=[contact.id])
        data = {'house': 'updatehouse'}
        res = self.client.patch(url, data)

        self.assertEqual(status.HTTP_200_OK, res.status_code)
        self.assertNotEqual(contact.house, res.data['house'])

    def test_delete_user_contact(self):
        """Test deleting the user contact for authenticated user"""

        self.client.force_authenticate(user=self.user)
        contact = create_contact(user=self.user)
        url = reverse('user:contact-detail', args=[contact.id])
        res = self.client.delete(url)

        self.assertEqual(status.HTTP_204_NO_CONTENT, res.status_code)

    def test_delete_only_own_contact(self):
        """Test deleting a contact only by it's owner"""
        self.client.force_authenticate(user=self.user)
        contact_1 = create_contact(user=self.user)
        contact_2 = create_contact(user=self.staff)
        url = reverse('user:contact-detail', args=[contact_2.id])
        url_own = reverse('user:contact-detail', args=[contact_1.id])

        res = self.client.delete(url)
        res_own = self.client.delete(url_own)

        self.assertEqual(status.HTTP_404_NOT_FOUND, res.status_code)
        self.assertEqual(status.HTTP_204_NO_CONTENT, res_own.status_code)

    def test_delete_any_contact_by_staff(self):
        """Test deleting any contact by staff"""
        self.client.force_authenticate(user=self.staff)
        contact = create_contact(user=self.user)
        url = reverse('user:contact-detail', args=[contact.id])
        res = self.client.delete(url)

        self.assertEqual(status.HTTP_204_NO_CONTENT, res.status_code)


