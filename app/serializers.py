from datetime import date
from typing import Dict, Any
from rest_framework import serializers
from .models import Room
from .models import Booking

class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = '__all__'


class BookingSerializer(serializers.ModelSerializer):
    room: serializers.PrimaryKeyRelatedField[Room] = serializers.PrimaryKeyRelatedField(
        queryset=Room.objects.all()
    )

    class Meta:
        model = Booking
        fields = '__all__'
        read_only_fields: tuple[str] = ['user', 'status']

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        arrival: date = attrs["arrival_date"]
        departure: date = attrs["departure_date"]
        room: Room = attrs["room"]

        overlapping: bool = Booking.objects.filter(
            room=room,
            status='Booked',
            arrival_date__lte=departure,
            departure_date__gte=arrival
        ).exists()

        if overlapping:
            raise serializers.ValidationError({
                "room": 'This room is already reserved'
            })

        return attrs
