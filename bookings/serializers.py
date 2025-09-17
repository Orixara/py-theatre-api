from django.utils import timezone
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from django.db import transaction

from theatre.serializers import PerformanceListSerializer

from bookings.models import Ticket, Reservation


class TicketSerializer(serializers.ModelSerializer):
    def validate(self, attrs):
        attrs = super().validate(attrs)

        if attrs["performance"].show_time <= timezone.now():
            raise ValidationError(
                {"performance": "Tickets cannot be booked for a past performance."}
            )

        Ticket.validate_tickets(
            attrs["row"],
            attrs["seat"],
            attrs["performance"].theatre_hall,
            ValidationError
        )
        if Ticket.objects.filter(
                performance=attrs["performance"],
                row=attrs["row"],
                seat=attrs["seat"]
        ).exists():
            raise ValidationError(
                {
                    "non_field_errors": ["This seat is already booked"]
                }
            )

        return attrs

    class Meta:
        model = Ticket
        fields = ("id", "row", "seat", "performance")


class TicketDetailSerializer(TicketSerializer):
    performance = PerformanceListSerializer(many=False, read_only=True)


class ReservationSerializer(serializers.ModelSerializer):
    tickets = TicketSerializer(many=True, write_only=True, allow_empty=False)
    reservation_tickets = TicketDetailSerializer(many=True, read_only=True)

    class Meta:
        model = Reservation
        fields = ("id", "tickets", "reservation_tickets", "created_at")

    def create(self, validated_data):
        with transaction.atomic():
            tickets_data = validated_data.pop("tickets")
            reservation = Reservation.objects.create(**validated_data)
            for ticket_data in tickets_data:
                Ticket.objects.create(reservation=reservation, **ticket_data)
            return reservation


class ReservationListSerializer(ReservationSerializer):
    reservation_tickets = TicketSerializer(many=True, read_only=True)
    
    class Meta:
        model = Reservation
        fields = ("id", "reservation_tickets", "created_at")
