import pytest
from rest_framework.test import APIClient
from django.contrib.auth.models import User


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user():
    return User.objects.create_user(username="test", password="test12345")


@pytest.fixture
def super_user():
    return User.objects.create_superuser(username='admin', password='admin12345')


@pytest.fixture
def auth_client(api_client, user):
    api_client.force_authenticate(user=user)
    return api_client


@pytest.fixture
def auth_super_user(api_client, super_user):
    api_client.force_authenticate(user=super_user)
    return api_client
