from datetime import date
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings

class Room(models.Model):
    number: int = models.PositiveIntegerField(unique=True)
    price_per_day: float = models.DecimalField(max_digits=10, decimal_places=2)
    number_of_seats: int = models.PositiveIntegerField()

    def __str__(self) -> str:
        return str(self.number)


class Booking(models.Model):
    room_status = [
        ("Booked", "booked"),
        ("Cancelled", "cancelled")
    ]

    user: AbstractUser = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='bookings')
    room: Room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='bookings')
    arrival_date: date = models.DateField()
    departure_date: date = models.DateField()
    status: str = models.CharField(max_length=9, choices=room_status)

    def __str__(self) -> str:
        return self.user.username

