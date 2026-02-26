from django.db import models
from django.conf import settings

class Room(models.Model):
    number = models.PositiveIntegerField(unique=True)
    price_per_day = models.DecimalField(max_digits=10, decimal_places=2)
    number_of_seats = models.PositiveIntegerField()

    def __str__(self):
        return str(self.number)


class Booking(models.Model):
    room_status = [
        ("Booked", "booked"),
        ("Cancelled", "cancelled")
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='bookings')
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='bookings')
    arrival_date = models.DateField()
    departure_date = models.DateField()
    status = models.CharField(max_length=9, choices=room_status)

    def __str__(self):
        return self.user.username

