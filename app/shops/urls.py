from django.urls import path

from .views import ShopUpdate, CategoryView, ShopView, ProductInfoView, ShopState

app_name = 'shops'

urlpatterns = [
    path('update/', ShopUpdate.as_view(), name='update'),
    path('categories/', CategoryView.as_view(), name='categories'),
    path('shops/', ShopView.as_view(), name='shops'),
    path('products/', ProductInfoView.as_view(), name='products'),
    path('state/', ShopState.as_view(), name='state'),

]
