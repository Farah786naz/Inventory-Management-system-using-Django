from .views import Userview
from django.urls import path, include

from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'users', Userview, basename='user')
urlpatterns = [
    path('', include(router.urls)),
]