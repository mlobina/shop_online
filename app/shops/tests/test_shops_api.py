from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient, APITestCase
from rest_framework import status
from rest_framework.utils import json

from core.models import Shop, Category, Product, ProductInfo, Parameter, ProductParameter

UPDATE_SHOPS_URL = reverse('shops:update')


def create_user(**params):
    return get_user_model().objects.create_user(**params)


class PublicShopsApiTests(TestCase):
    """Test the shops API (public, without authentication)"""

    def setUp(self):
        self.client = APIClient()

    def test_update_price_list_unauthorized(self):
        """Test that authentication is required for users"""
        res = self.client.get(UPDATE_SHOPS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateShopsApiTests(TestCase):
    """Test API requests that require authentication"""

    def setUp(self):
        self.user = create_user(
            email='test@mail.com',
            password='testpass',
            name='Test',
            company='testcompany',
            position='testposition',
            type='shop',
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_update_price_list_success(self):
        """Test updating price list for logged in user"""
        url = "url"
        res = self.client.post(UPDATE_SHOPS_URL,
                               {'url': f'{url}'}

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.json()['Status'], True)
