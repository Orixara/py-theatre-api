from django.test import TestCase
from django.contrib.auth import get_user_model
from bookings.models import Reservation, Ticket
from bookings.serializers import (
    TicketSerializer,
    TicketDetailSerializer,
    ReservationSerializer,
    ReservationListSerializer,
)
from theatre.models import Play, TheatreHall, Performance
from datetime import datetime


User = get_user_model()


class TicketSerializerTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )
        self.play = Play.objects.create(
            title="Hamlet", description="A famous Shakespeare play"
        )
        self.theatre_hall = TheatreHall.objects.create(
            name="Main Hall", rows=10, seats_in_row=20
        )
        self.performance = Performance.objects.create(
            play=self.play,
            theatre_hall=self.theatre_hall,
            show_time=datetime(2024, 12, 25, 19, 30),
        )
        self.reservation = Reservation.objects.create(user=self.user)

    def test_ticket_serializer_valid(self):
        """Test valid ticket serialization"""
        data = {"row": 5, "seat": 10, "performance": self.performance.id}
        serializer = TicketSerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_ticket_serializer_invalid_row(self):
        """Test ticket serializer validation for invalid row"""
        data = {"row": 15, "seat": 10, "performance": self.performance.id}
        serializer = TicketSerializer(data=data)
        self.assertFalse(serializer.is_valid())

    def test_ticket_serializer_invalid_seat(self):
        """Test ticket serializer validation for invalid seat"""
        data = {"row": 5, "seat": 25, "performance": self.performance.id}
        serializer = TicketSerializer(data=data)
        self.assertFalse(serializer.is_valid())

    def test_ticket_serializer_seat_already_booked(self):
        """Test ticket serializer validation for already booked seat"""
        Ticket.objects.create(
            row=5, seat=10, performance=self.performance, reservation=self.reservation
        )

        data = {"row": 5, "seat": 10, "performance": self.performance.id}
        serializer = TicketSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("This seat is already booked", str(serializer.errors))

    def test_ticket_detail_serializer_output(self):
        """Test ticket detail serializer includes performance details"""
        ticket = Ticket.objects.create(
            row=5, seat=10, performance=self.performance, reservation=self.reservation
        )
        serializer = TicketDetailSerializer(ticket)
        self.assertIn("performance", serializer.data)
        self.assertEqual(serializer.data["row"], 5)
        self.assertEqual(serializer.data["seat"], 10)


class ReservationSerializerTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )
        self.play = Play.objects.create(
            title="Hamlet", description="A famous Shakespeare play"
        )
        self.theatre_hall = TheatreHall.objects.create(
            name="Main Hall", rows=10, seats_in_row=20
        )
        self.performance = Performance.objects.create(
            play=self.play,
            theatre_hall=self.theatre_hall,
            show_time=datetime(2024, 12, 25, 19, 30),
        )

    def test_reservation_serializer_valid(self):
        """Test valid reservation creation with tickets"""
        data = {
            "tickets": [
                {"row": 5, "seat": 10, "performance": self.performance.id},
                {"row": 5, "seat": 11, "performance": self.performance.id},
            ]
        }
        serializer = ReservationSerializer(data=data)
        self.assertTrue(serializer.is_valid())

        reservation = serializer.save(user=self.user)
        self.assertEqual(reservation.user, self.user)
        self.assertEqual(reservation.reservation_tickets.count(), 2)

    def test_reservation_serializer_empty_tickets(self):
        """Test reservation serializer fails with empty tickets"""
        data = {"tickets": []}
        serializer = ReservationSerializer(data=data)
        self.assertFalse(serializer.is_valid())

    def test_reservation_serializer_invalid_ticket(self):
        """Test reservation serializer fails with invalid ticket"""
        data = {
            "tickets": [{"row": 15, "seat": 10, "performance": self.performance.id}]
        }
        serializer = ReservationSerializer(data=data)
        self.assertFalse(serializer.is_valid())

    def test_reservation_serializer_duplicate_seats(self):
        """Test reservation serializer with duplicate seats in same reservation"""
        reservation = Reservation.objects.create(user=self.user)
        Ticket.objects.create(
            row=5, seat=10, performance=self.performance, reservation=reservation
        )

        data = {"tickets": [{"row": 5, "seat": 10, "performance": self.performance.id}]}
        serializer = ReservationSerializer(data=data)
        self.assertFalse(serializer.is_valid())

    def test_reservation_serializer_output(self):
        """Test reservation serializer output includes tickets"""
        reservation = Reservation.objects.create(user=self.user)
        ticket = Ticket.objects.create(
            row=5, seat=10, performance=self.performance, reservation=reservation
        )

        serializer = ReservationSerializer(reservation)
        self.assertIn("reservation_tickets", serializer.data)
        self.assertIn("created_at", serializer.data)
        self.assertEqual(len(serializer.data["reservation_tickets"]), 1)

    def test_reservation_list_serializer(self):
        """Test reservation list serializer has simplified output"""
        reservation = Reservation.objects.create(user=self.user)
        ticket = Ticket.objects.create(
            row=5, seat=10, performance=self.performance, reservation=reservation
        )

        serializer = ReservationListSerializer(reservation)
        self.assertIn("reservation_tickets", serializer.data)
        self.assertIn("created_at", serializer.data)
        self.assertNotIn("tickets", serializer.data)

    def test_reservation_atomic_transaction(self):
        """Test that reservation creation is atomic"""
        data = {
            "tickets": [
                {"row": 5, "seat": 10, "performance": self.performance.id},
                {"row": 15, "seat": 11, "performance": self.performance.id},
            ]
        }

        serializer = ReservationSerializer(data=data)
        self.assertFalse(serializer.is_valid())

        self.assertEqual(Reservation.objects.count(), 0)
        self.assertEqual(Ticket.objects.count(), 0)
