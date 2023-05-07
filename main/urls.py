from django.urls import path
from rest_framework_jwt.views import ObtainJSONWebToken, RefreshJSONWebToken

from .views import RegisterAPI, RevokeTokenView, RestaurantCreateView, MenuListView, VoteView, CurrentDayMenuView

urlpatterns = [
    path('register/', RegisterAPI.as_view(), name='register'),
    path('signin/', ObtainJSONWebToken.as_view(), name='signin'),
    path('refresh/', RefreshJSONWebToken.as_view(), name='refresh'),
    path('revoke/', RevokeTokenView.as_view(), name='revoke'),
    path('restaurant/', RestaurantCreateView.as_view(), name='restaurant'),
    path('menu/', MenuListView.as_view(), name='menu'),
    path('menu/<int:restaurant_id>/', MenuListView.as_view(), name='menu-by-restaurant'),
    path('vote/', VoteView.as_view(), name='vote'),
    path('menu-today/', CurrentDayMenuView.as_view(), name='menu-today'),
    path('menu-today/<int:restaurant_id>/', CurrentDayMenuView.as_view(), name='menu-today-by-restaurant'),
]
