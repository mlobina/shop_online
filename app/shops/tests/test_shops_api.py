from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from rest_framework.utils import json

from core.models import Shop, Category, Product, ProductInfo, Parameter, ProductParameter

UPDATE_SHOPS_URL = reverse('shops:update')
SHOP_STATE_URL = reverse('shops:state')


def create_user(**params):
    return get_user_model().objects.create_user(**params)


def create_shop(**params):
    return Shop.objects.create(**params)


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
        self.partner = create_user(
            email='partner@mail.com',
            password='testpass',
            name='Test',
            company='testcompany',
            position='testposition',
            type='shop',
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.partner)

    def test_update_price_list_success(self):
        """Test updating price list for logged in user"""

        url = "https://raw.githubusercontent.com/mlobina/shop_online/master/data/shop1.yaml"
        false_url = "falsefalse"
        res = self.client.post(UPDATE_SHOPS_URL,
                               {'url': f'{url}'})
        false_res = self.client.post(UPDATE_SHOPS_URL,
                               {'url': f'{false_url}'})

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.json()['Status'], True)
        self.assertEqual(false_res.json()['Status'], False)

    def test_shop_state_success(self):
        """Test getting shop state by logged in user"""
        self.shop = Shop.objects.create(
            name='testshop',
            url='shopurl',
            user=self.partner,
            state=True)
        res = self.client.get(SHOP_STATE_URL)
        change_res = self.client.post(SHOP_STATE_URL,
                               {"Status": False})
        res_json = res.json()
        change_res_json = change_res.json()

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(change_res.status_code, status.HTTP_200_OK)
        self.assertEqual(res_json['id'], self.shop.id)
        self.assertEqual(res_json['state'], self.shop.state)
        self.assertEqual(change_res_json['Status'], False)





