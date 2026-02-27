import pytest
from datetime import date, timedelta

from rest_framework import status
from .models import Room, Booking


@pytest.mark.django_db
def test_create_room(api_client):
    Room.objects.create(number=10, price_per_day=400, number_of_seats=10)
    Room.objects.create(number=101, price_per_day=800, number_of_seats=16)

    url = "/api/rooms/"
    response = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 2
    assert response.data[1]["number"] == 101


@pytest.mark.django_db
def test_no_access_no_auth_booking(api_client):
    url = "/api/bookings/"
    response = api_client.get(url)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_create_booking_auth(user, auth_client):
    room = Room.objects.create(number=10, price_per_day=400, number_of_seats=10)

    url = "/api/bookings/"
    data = {
        "room": room.id,
        "arrival_date": date.today(),
        "departure_date": date.today() + timedelta(days=3),
    }
    response = auth_client.post(url, data)

    print(date.today())

    assert response.status_code == status.HTTP_201_CREATED
    assert Booking.objects.count() == 1
    assert Booking.objects.first().user == user


@pytest.mark.django_db
def test_booking_collision(user, auth_client):
    room = Room.objects.create(number=10, price_per_day=400, number_of_seats=10)

    Booking.objects.create(
        user=user,
        room=room,
        arrival_date=date.today(),
        departure_date=date.today() + timedelta(days=3),
        status="Booked",
    )

    url = "/api/bookings"
    data = {
        "room": room.id,
        "arrival_date": date.today() + timedelta(days=1),
        "departure_date": date.today() + timedelta(days=3),
    }

    response = auth_client.post(url, data)

    assert response.status_code != status.HTTP_201_CREATED
    assert Booking.objects.count() == 1


@pytest.mark.django_db
def test_cancel_booking_auth(user, auth_client):
    room = Room.objects.create(number=10, price_per_day=400, number_of_seats=10)

    booking = Booking.objects.create(
        user=user,
        room=room,
        arrival_date=date.today(),
        departure_date=date.today() + timedelta(days=3),
        status="Booked",
    )

    url = f"/api/bookings/{booking.id}/"
    response = auth_client.delete(url)

    booking.refresh_from_db()

    assert Booking.objects.count() == 1
    assert booking.status == "Cancelled"
