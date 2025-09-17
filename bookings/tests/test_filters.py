from django.test import TestCase
from django.contrib.auth import get_user_model
from bookings.models import Reservation, Ticket
from bookings.filters import ReservationFilter, TicketFilter
from theatre.models import Play, TheatreHall, Performance
from datetime import datetime, date


User = get_user_model()


class ReservationFilterTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(
            username="user1", email="user1@example.com", password="pass123"
        )
        self.user2 = User.objects.create_user(
            username="user2", email="user2@example.com", password="pass123"
        )

        self.play1 = Play.objects.create(title="Hamlet", description="Shakespeare")
        self.play2 = Play.objects.create(
            title="Macbeth", description="Another Shakespeare"
        )

        self.theatre_hall = TheatreHall.objects.create(
            name="Main Hall", rows=10, seats_in_row=20
        )

        self.performance1 = Performance.objects.create(
            play=self.play1,
            theatre_hall=self.theatre_hall,
            show_time=datetime(2024, 12, 25, 19, 30),
        )
        self.performance2 = Performance.objects.create(
            play=self.play2,
            theatre_hall=self.theatre_hall,
            show_time=datetime(2024, 12, 26, 20, 0),
        )

        self.reservation1 = Reservation.objects.create(user=self.user1)
        self.reservation2 = Reservation.objects.create(user=self.user2)

        self.ticket1 = Ticket.objects.create(
            row=5, seat=10, performance=self.performance1, reservation=self.reservation1
        )
        self.ticket2 = Ticket.objects.create(
            row=6, seat=11, performance=self.performance2, reservation=self.reservation2
        )

        from django.utils import timezone

        self.reservation1.created_at = timezone.make_aware(
            datetime(2024, 12, 20, 10, 0)
        )
        self.reservation1.save()
        self.reservation2.created_at = timezone.make_aware(
            datetime(2024, 12, 21, 15, 0)
        )
        self.reservation2.save()

    def test_filter_reservation_by_created_from(self):
        """Test filtering reservations from specific date"""
        filter_data = {"created_from": "2024-12-21"}
        reservation_filter = ReservationFilter(
            data=filter_data, queryset=Reservation.objects.all()
        )
        self.assertTrue(reservation_filter.is_valid())
        filtered_reservations = reservation_filter.qs
        self.assertEqual(filtered_reservations.count(), 1)
        self.assertEqual(filtered_reservations.first(), self.reservation2)

    def test_filter_reservation_by_created_to(self):
        """Test filtering reservations to specific date"""
        filter_data = {"created_to": "2024-12-20"}
        reservation_filter = ReservationFilter(
            data=filter_data, queryset=Reservation.objects.all()
        )
        self.assertTrue(reservation_filter.is_valid())
        filtered_reservations = reservation_filter.qs
        self.assertEqual(filtered_reservations.count(), 1)
        self.assertEqual(filtered_reservations.first(), self.reservation1)

    def test_filter_reservation_by_created_date_range(self):
        """Test filtering reservations by date range"""
        filter_data = {"created_from": "2024-12-20", "created_to": "2024-12-21"}
        reservation_filter = ReservationFilter(
            data=filter_data, queryset=Reservation.objects.all()
        )
        self.assertTrue(reservation_filter.is_valid())
        filtered_reservations = reservation_filter.qs
        self.assertEqual(filtered_reservations.count(), 2)

    def test_filter_reservation_by_play_title(self):
        """Test filtering reservations by play title (case insensitive)"""
        filter_data = {"play_title": "hamlet"}
        reservation_filter = ReservationFilter(
            data=filter_data, queryset=Reservation.objects.all()
        )
        self.assertTrue(reservation_filter.is_valid())
        filtered_reservations = reservation_filter.qs
        self.assertEqual(filtered_reservations.count(), 1)
        self.assertEqual(filtered_reservations.first(), self.reservation1)

    def test_filter_reservation_by_play_title_partial(self):
        """Test filtering reservations by partial play title"""
        filter_data = {"play_title": "beth"}
        reservation_filter = ReservationFilter(
            data=filter_data, queryset=Reservation.objects.all()
        )
        self.assertTrue(reservation_filter.is_valid())
        filtered_reservations = reservation_filter.qs
        self.assertEqual(filtered_reservations.count(), 1)
        self.assertEqual(filtered_reservations.first(), self.reservation2)

    def test_filter_reservation_by_performance(self):
        """Test filtering reservations by specific performance"""
        filter_data = {"performance": self.performance1.id}
        reservation_filter = ReservationFilter(
            data=filter_data, queryset=Reservation.objects.all()
        )
        self.assertTrue(reservation_filter.is_valid())
        filtered_reservations = reservation_filter.qs
        self.assertEqual(filtered_reservations.count(), 1)
        self.assertEqual(filtered_reservations.first(), self.reservation1)

    def test_filter_reservation_combined_filters(self):
        """Test filtering reservations with combined filters"""
        filter_data = {"created_from": "2024-12-20", "play_title": "hamlet"}
        reservation_filter = ReservationFilter(
            data=filter_data, queryset=Reservation.objects.all()
        )
        self.assertTrue(reservation_filter.is_valid())
        filtered_reservations = reservation_filter.qs
        self.assertEqual(filtered_reservations.count(), 1)
        self.assertEqual(filtered_reservations.first(), self.reservation1)

    def test_filter_reservation_no_matches(self):
        """Test filtering reservations with no matches"""
        filter_data = {"play_title": "nonexistent"}
        reservation_filter = ReservationFilter(
            data=filter_data, queryset=Reservation.objects.all()
        )
        self.assertTrue(reservation_filter.is_valid())
        filtered_reservations = reservation_filter.qs
        self.assertEqual(filtered_reservations.count(), 0)

    def test_filter_reservation_distinct_handling(self):
        """Test that distinct=True works properly for related field filters"""
        performance3 = Performance.objects.create(
            play=self.play1,
            theatre_hall=self.theatre_hall,
            show_time=datetime(2024, 12, 27, 19, 30),
        )
        Ticket.objects.create(
            row=7, seat=12, performance=performance3, reservation=self.reservation1
        )

        filter_data = {"play_title": "hamlet"}
        reservation_filter = ReservationFilter(
            data=filter_data, queryset=Reservation.objects.all()
        )
        self.assertTrue(reservation_filter.is_valid())
        filtered_reservations = reservation_filter.qs
        self.assertEqual(filtered_reservations.count(), 1)
        self.assertEqual(filtered_reservations.first(), self.reservation1)


class TicketFilterTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="pass123"
        )

        self.play = Play.objects.create(title="Test Play", description="Description")
        self.theatre_hall = TheatreHall.objects.create(
            name="Main Hall", rows=10, seats_in_row=20
        )

        self.performance1 = Performance.objects.create(
            play=self.play,
            theatre_hall=self.theatre_hall,
            show_time=datetime(2024, 12, 25, 19, 30),
        )
        self.performance2 = Performance.objects.create(
            play=self.play,
            theatre_hall=self.theatre_hall,
            show_time=datetime(2024, 12, 26, 20, 0),
        )
        self.performance3 = Performance.objects.create(
            play=self.play,
            theatre_hall=self.theatre_hall,
            show_time=datetime(2024, 12, 27, 21, 0),
        )

        self.reservation = Reservation.objects.create(user=self.user)

        self.ticket1 = Ticket.objects.create(
            row=5, seat=10, performance=self.performance1, reservation=self.reservation
        )
        self.ticket2 = Ticket.objects.create(
            row=6, seat=11, performance=self.performance2, reservation=self.reservation
        )
        self.ticket3 = Ticket.objects.create(
            row=7, seat=12, performance=self.performance3, reservation=self.reservation
        )

    def test_filter_ticket_by_show_date_from(self):
        """Test filtering tickets from specific show date"""
        filter_data = {"show_date_from": "2024-12-26"}
        ticket_filter = TicketFilter(data=filter_data, queryset=Ticket.objects.all())
        self.assertTrue(ticket_filter.is_valid())
        filtered_tickets = ticket_filter.qs
        self.assertEqual(filtered_tickets.count(), 2)
        self.assertIn(self.ticket2, filtered_tickets)
        self.assertIn(self.ticket3, filtered_tickets)
        self.assertNotIn(self.ticket1, filtered_tickets)

    def test_filter_ticket_by_show_date_to(self):
        """Test filtering tickets to specific show date"""
        filter_data = {"show_date_to": "2024-12-26"}
        ticket_filter = TicketFilter(data=filter_data, queryset=Ticket.objects.all())
        self.assertTrue(ticket_filter.is_valid())
        filtered_tickets = ticket_filter.qs
        self.assertEqual(filtered_tickets.count(), 2)
        self.assertIn(self.ticket1, filtered_tickets)
        self.assertIn(self.ticket2, filtered_tickets)
        self.assertNotIn(self.ticket3, filtered_tickets)

    def test_filter_ticket_by_show_date_range(self):
        """Test filtering tickets by show date range"""
        filter_data = {"show_date_from": "2024-12-25", "show_date_to": "2024-12-26"}
        ticket_filter = TicketFilter(data=filter_data, queryset=Ticket.objects.all())
        self.assertTrue(ticket_filter.is_valid())
        filtered_tickets = ticket_filter.qs
        self.assertEqual(filtered_tickets.count(), 2)
        self.assertIn(self.ticket1, filtered_tickets)
        self.assertIn(self.ticket2, filtered_tickets)
        self.assertNotIn(self.ticket3, filtered_tickets)

    def test_filter_ticket_exact_date(self):
        """Test filtering tickets for exact date"""
        filter_data = {"show_date_from": "2024-12-26", "show_date_to": "2024-12-26"}
        ticket_filter = TicketFilter(data=filter_data, queryset=Ticket.objects.all())
        self.assertTrue(ticket_filter.is_valid())
        filtered_tickets = ticket_filter.qs
        self.assertEqual(filtered_tickets.count(), 1)
        self.assertEqual(filtered_tickets.first(), self.ticket2)

    def test_filter_ticket_no_matches(self):
        """Test filtering tickets with no matches"""
        filter_data = {"show_date_from": "2025-01-01"}
        ticket_filter = TicketFilter(data=filter_data, queryset=Ticket.objects.all())
        self.assertTrue(ticket_filter.is_valid())
        filtered_tickets = ticket_filter.qs
        self.assertEqual(filtered_tickets.count(), 0)

    def test_filter_ticket_all_matches(self):
        """Test filtering that returns all tickets"""
        filter_data = {"show_date_from": "2024-12-01"}
        ticket_filter = TicketFilter(data=filter_data, queryset=Ticket.objects.all())
        self.assertTrue(ticket_filter.is_valid())
        filtered_tickets = ticket_filter.qs
        self.assertEqual(filtered_tickets.count(), 3)

    def test_filter_ticket_invalid_date_format(self):
        """Test filtering with invalid date format"""
        filter_data = {"show_date_from": "invalid-date"}
        ticket_filter = TicketFilter(data=filter_data, queryset=Ticket.objects.all())
        self.assertFalse(ticket_filter.is_valid())
        self.assertIn("show_date_from", ticket_filter.errors)

    def test_filter_ticket_empty_filters(self):
        """Test filtering with empty filter data"""
        filter_data = {}
        ticket_filter = TicketFilter(data=filter_data, queryset=Ticket.objects.all())
        self.assertTrue(ticket_filter.is_valid())
        filtered_tickets = ticket_filter.qs
        self.assertEqual(filtered_tickets.count(), 3)
