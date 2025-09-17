from rest_framework.permissions import IsAuthenticated
from rest_framework.throttling import UserRateThrottle
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from bookings.models import Reservation, Ticket
from bookings.serializers import (
    ReservationSerializer,
    ReservationListSerializer,
    TicketSerializer,
    TicketDetailSerializer
)
from bookings.filters import ReservationFilter, TicketFilter

class ReservationViewSet(ModelViewSet):
    serializer_class = ReservationSerializer
    permission_classes = [IsAuthenticated]

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = ReservationFilter
    ordering_fields = ["created_at", "id"]
    ordering = ["-created_at"]
    
    def get_search_fields(self):
        if self.request.user.is_staff:
            return [
                "reservation_tickets__performance__play__title",
                "user__email", "user__first_name", "user__last_name"
            ]
        return ["reservation_tickets__performance__play__title"]

    def get_queryset(self):
        base_queryset = Reservation.objects.select_related("user").prefetch_related(
            "reservation_tickets__performance__play",
            "reservation_tickets__performance__theatre_hall"
        )
        
        if self.request.user.is_staff:
            return base_queryset
        return base_queryset.filter(user=self.request.user)

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

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = TicketFilter
    search_fields = ["performance__play__title"]
    ordering_fields = ["performance__show_time", "row", "seat"]
    ordering = ["performance__show_time", "row", "seat"]

    def get_queryset(self):
        base_queryset = Ticket.objects.select_related(
            "performance__play",
            "performance__theatre_hall",
            "reservation__user"
        )
        
        if self.request.user.is_staff:
            return base_queryset
        return base_queryset.filter(reservation__user=self.request.user)

    def get_serializer_class(self):
        if self.action == "list":
            return TicketSerializer
        return TicketDetailSerializer