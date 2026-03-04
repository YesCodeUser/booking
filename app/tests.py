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
    auth_client.delete(url)

    booking.refresh_from_db()

    assert Booking.objects.count() == 1
    assert booking.status == "Cancelled"


@pytest.mark.django_db
def test_staff_see_all_bookings(auth_super_user, super_user, user):
    room1 = Room.objects.create(number=10, price_per_day=400, number_of_seats=10)
    room2 = Room.objects.create(number=11, price_per_day=400, number_of_seats=10)

    Booking.objects.create(
        user=super_user,
        room=room1,
        arrival_date=date.today(),
        departure_date=date.today() + timedelta(days=3),
        status="Booked",
    )

    Booking.objects.create(
        user=user,
        room=room2,
        arrival_date=date.today(),
        departure_date=date.today() + timedelta(days=3),
        status="Booked",
    )

    url = '/api/bookings/'
    response = auth_super_user.get(url)

    assert Booking.objects.count() == 2
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_staff_create_booking_to_another_user(auth_super_user, user):
    room = Room.objects.create(number=10, price_per_day=400, number_of_seats=10)

    data = {
        'user': user.id,
        "room": room.id,
        "arrival_date": date.today(),
        "departure_date": date.today() + timedelta(days=3),
    }

    url = '/api/bookings/'
    response = auth_super_user.post(url, data)

    assert response.status_code == status.HTTP_201_CREATED
    assert Booking.objects.count() == 1
    assert Booking.objects.first().user == user


@pytest.mark.django_db
def test_staff_cancel_booking_another_user(auth_super_user, user):
    room = Room.objects.create(number=10, price_per_day=400, number_of_seats=10)

    booking = Booking.objects.create(
        user=user,
        room=room,
        arrival_date=date.today(),
        departure_date=date.today() + timedelta(days=3),
        status="Booked",
    )

    url = f'/api/bookings/{booking.id}/'
    auth_super_user.delete(url)

    booking.refresh_from_db()

    assert booking.status == "Cancelled"


@pytest.mark.django_db
def test_staff_update_booking_another_user(auth_super_user, user, super_user):
    room1 = Room.objects.create(number=10, price_per_day=400, number_of_seats=10)
    room2 = Room.objects.create(number=11, price_per_day=400, number_of_seats=10)

    booking = Booking.objects.create(
        user=user,
        room=room1,
        arrival_date=date.today(),
        departure_date=date.today() + timedelta(days=3),
        status="Booked",
    )

    data = {
        'user': super_user.id,
        'room': room2.id,
        'arrival_date': date.today() + timedelta(days=10),
        'departure_date': date.today() + timedelta(days=20),
        'status': "Cancelled"
    }

    url = f'/api/bookings/{booking.id}/'
    response = auth_super_user.patch(url, data)

    booking.refresh_from_db()

    assert response.status_code == status.HTTP_200_OK
    assert booking.user == super_user
    assert booking.room == room2
    assert booking.arrival_date == date.today() + timedelta(days=10)
    assert booking.departure_date == date.today() + timedelta(days=20)
    assert booking.status == 'Cancelled'
