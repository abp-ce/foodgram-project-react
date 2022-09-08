from django.urls import include, path
from rest_framework import routers

from .views import FoodgramUserViewSet

app_name = 'users'

router = routers.DefaultRouter()
router.register(r'users', FoodgramUserViewSet, basename='users')

urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('djoser.urls.authtoken')),
]
