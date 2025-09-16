from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from django.db import transaction

from theatre.serializers import PerformanceListSerializer

from bookings.models import Ticket, Reservation


class TicketSerializer(serializers.ModelSerializer):
    def validate(self, attrs):
        attrs = super().validate(attrs)
        Ticket.validate_tickets(
            attrs["row"],
            attrs["seat"],
            attrs["performance"].theatre_hall,
            ValidationError
        )
        return attrs

    class Meta:
        model = Ticket
        fields = ("id", "row", "seat", "performance")


class TicketDetailSerializer(TicketSerializer):
    performance = PerformanceListSerializer(many=False, read_only=True)


class TakenSeatsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = ("row", "seat")


class ReservationSerializer(serializers.ModelSerializer):
    tickets = TicketSerializer(many=True, read_only=False, allow_empty=False)

    class Meta:
        model = Reservation
        fields = ("id", "tickets", "created_at")

    def create(self, validated_data):
        with transaction.atomic():
            tickets_data = validated_data.pop("tickets")
            reservation = Reservation.objects.create(**validated_data)
            for ticket_data in tickets_data:
                Ticket.objects.create(reservation=reservation, **ticket_data)
            return reservation


class ReservationListSerializer(ReservationSerializer):
    tickets = TicketDetailSerializer(many=True, read_only=True)