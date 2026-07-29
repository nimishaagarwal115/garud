from django.urls import path
from account import views
from catalogue.views import *
from catalogue.function import *
from core.base.functions import *
urlpatterns = [  
    path('wishlist/', WishlistView.as_view(), name='wishlist'),
    path('add-to-wishlist/', add_to_wishlist, name='add_to_wishlist'),
    path('remove-from-wishlist/', remove_from_wishlist, name='remove_from_wishlist'),
]