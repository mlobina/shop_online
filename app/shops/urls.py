from django.urls import path

from shops.views import ShopUpdate

app_name = 'shops'

urlpatterns = [
    path('update/', ShopUpdate.as_view(), name='update'),

]
