from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from rest_framework.utils import json

from core.models import Shop, Category, Product, ProductInfo, Parameter, ProductParameter

BASKET_URL = reverse('clients:basket')


def create_user(**params):
    return get_user_model().objects.create_user(**params)


def create_product(**params):
    return ProductInfo.objects.create(**params)



class PublicClientsApiTests(TestCase):
    """Test the clients API (public, without authentication)"""

    def setUp(self):
        self.client = APIClient()

    def test_basket_unauthorized(self):
        """Test that authentication is required for users"""
        res = self.client.get(BASKET_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateClientsApiTests(TestCase):
    """Test API requests that require authentication"""

    def setUp(self):
        self.user = create_user(
            email='user@mail.com',
            password='testpass',
            name='Test',
            company='testcompany',
            position='testposition',
            type='buyer',
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retrieve_basket_success(self):
        """Test retrieving basket for logged in user"""
        res = self.client.get(BASKET_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)


    # def test_add_items_to_basket(self):
    #     """Test adding item to basket for logged in user"""
    #     test_item = create_product(
    #         external_id='test_id',
    #         quantity=1,
    #         price=11,
    #         price_rrc=112
    #     )



