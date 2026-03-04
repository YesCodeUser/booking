from django.db import transaction
from typing import Dict, Any
from rest_framework import serializers
from .models import Room
from .models import Booking


class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = "__all__"


class BookingSerializer(serializers.ModelSerializer):
    room: serializers.PrimaryKeyRelatedField[Room] = serializers.PrimaryKeyRelatedField(
        queryset=Room.objects.all()
    )

    class Meta:
        model = Booking
        fields = "__all__"
        read_only_fields: tuple[str] = ["user", "status"]

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        instance = self.instance

        arrival = attrs.get("arrival_date", instance.arrival_date if instance else None)
        departure = attrs.get('departure_date', instance.departure_date if instance else None)
        room = attrs.get('room', instance.room if instance else None)

        if not all([arrival, departure, room]):
            raise serializers.ValidationError('Missing requirements fields.')


        if arrival >= departure:
            raise serializers.ValidationError(
                {
                    "departure_date": "The departure date must be later than the arrival date."
                }
            )

        with transaction.atomic():
            Room.objects.select_for_update().get(id=room.id)

            overlapping = Booking.objects.filter(
                room=room,
                status="Booked",
                arrival_date__lt=departure,
                departure_date__gt=arrival,
            )

            if instance:
                overlapping = overlapping.exclude(pk=instance.pk)

            if overlapping.exists():
                raise serializers.ValidationError(f"Room: {room.id} is already reserved")

        return attrs
