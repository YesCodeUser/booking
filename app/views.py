from datetime import datetime, date
from typing import Any

from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.filters import OrderingFilter
from rest_framework.viewsets import ReadOnlyModelViewSet, ModelViewSet
from rest_framework.permissions import IsAuthenticated, AllowAny
from django_filters.rest_framework import DjangoFilterBackend

from .models import Room
from .models import Booking
from .serializers import RoomSerializer
from .serializers import BookingSerializer


class RoomViewSet(ReadOnlyModelViewSet):
    permission_classes: list[type] = [AllowAny]
    filter_backends: list[type] = [DjangoFilterBackend, OrderingFilter]
    filterset_fields: list[str] = ["price_per_day", "number_of_seats"]
    ordering_fields: list[str] = ["price_per_day", "number_of_seats"]
    queryset = Room.objects.all()
    serializer_class = RoomSerializer

    @action(detail=False, methods=["get"], url_path="available")
    def available(self, request: Any) -> Response:
        arrival_str: str | None = self.request.query_params.get("arrival")
        departure_str: str | None = self.request.query_params.get("departure")

        if not arrival_str or not departure_str:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        try:
            arrival_date: date = datetime.strptime(arrival_str, "%Y-%m-%d").date()
            departure_date: date = datetime.strptime(departure_str, "%Y-%m-%d").date()
        except ValueError:
            raise ValidationError("Wrong date format")

        if arrival_date > departure_date:
            raise ValidationError("Arrival date must be later than departure date")

        free_rooms = Room.objects.exclude(
            bookings__status="Booked",
            bookings__arrival_date__lt=departure_date,
            bookings__departure_date__gt=arrival_date,
        ).distinct()

        serializer = self.get_serializer(free_rooms, many=True)
        return Response(serializer.data)


class BookingViewSet(ModelViewSet):
    permission_classes: list[type] = [IsAuthenticated]
    queryset = Booking.objects.none()
    serializer_class = BookingSerializer

    def get_queryset(self) -> Any:
        user = self.request.user
        if user.is_staff:
            return Booking.objects.all()
        return Booking.objects.filter(user=self.request.user)

    def perform_create(self, serializer) -> None:
        target_user = self.request.user
        request_user_id = self.request.data.get('user')

        if request_user_id and self.request.user.is_staff:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            try:
                target_user = User.objects.get(id=request_user_id)
            except User.DoesNotExist:
                raise ValidationError(f'User with id: {request_user_id} is not exists')

        serializer.save(user=target_user, status='Booked')

    def perform_destroy(self, instance) -> None:
        if instance.user != self.request.user and not self.request.user.is_staff:
            raise PermissionDenied("Cannot delete other people's reservations")
        if instance.status != "Booked":
            raise ValidationError("There is no reservations anyway")

        instance.status = "Cancelled"
        instance.save()

    def perform_update(self, serializer):
        instance = self.get_object()

        if instance.user != self.request.user and not self.request.user.is_staff:
            raise PermissionDenied("Cannot edit other people's reservations")

        update_kwargs = {}

        if self.request.user.is_staff:
            new_user_id = self.request.data.get('user')
            new_status = self.request.data.get('status')

            if new_status:
                update_kwargs['status'] = new_status

            if new_user_id:
                from django.contrib.auth import get_user_model

                User = get_user_model()
                try:
                    update_kwargs['user'] = User.objects.get(id=new_user_id)
                except User.DoesNotExist:
                    raise ValidationError(f'User with id: {new_user_id} is not exists')


        serializer.save(**update_kwargs)
