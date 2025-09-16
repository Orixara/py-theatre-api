from rest_framework.permissions import IsAuthenticated
from rest_framework.throttling import UserRateThrottle
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from bookings.models import Reservation, Ticket
from bookings.serializers import (
    ReservationSerializer,
    ReservationListSerializer,
    TicketSerializer,
    TicketDetailSerializer
)


class ReservationViewSet(ModelViewSet):
    serializer_class = ReservationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Reservation.objects.all()
        return Reservation.objects.filter(user=user)

    def get_serializer_class(self):
        if self.action == "list":
            return ReservationListSerializer
        return ReservationSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_throttle_classes(self):
        if self.action == "create":
            return [UserRateThrottle]
        return []


class TicketViewSet(ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Ticket.objects.all()
        return Ticket.objects.filter(reservation__user=user)

    def get_serializer_class(self):
        if self.action == "list":
            return TicketSerializer
        return TicketDetailSerializer