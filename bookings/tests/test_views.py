from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken
from bookings.models import Reservation, Ticket
from theatre.models import Play, TheatreHall, Performance
from datetime import datetime


User = get_user_model()


class BaseBookingAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )
        self.admin_user = User.objects.create_superuser(
            username="admin", email="admin@example.com", password="adminpass123"
        )
        self.other_user = User.objects.create_user(
            username="otheruser", email="other@example.com", password="otherpass123"
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

    def authenticate_user(self, user=None):
        if user is None:
            user = self.user
        refresh = RefreshToken.for_user(user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")

    def authenticate_admin(self):
        self.authenticate_user(self.admin_user)


class ReservationViewSetTest(BaseBookingAPITest):
    def setUp(self):
        super().setUp()
        self.reservation = Reservation.objects.create(user=self.user)
        self.ticket = Ticket.objects.create(
            row=5, seat=10, performance=self.performance, reservation=self.reservation
        )

    def test_list_reservations_authenticated(self):
        """Test authenticated user can list their own reservations"""
        self.authenticate_user()
        url = reverse("bookings:reservation-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_list_reservations_unauthenticated(self):
        """Test unauthenticated user cannot list reservations"""
        url = reverse("bookings:reservation-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_reservation(self):
        """Test creating a new reservation"""
        self.authenticate_user()
        url = reverse("bookings:reservation-list")
        data = {"tickets": [{"row": 3, "seat": 15, "performance": self.performance.id}]}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Reservation.objects.count(), 2)

    def test_create_reservation_invalid_seat(self):
        """Test creating reservation with invalid seat fails"""
        self.authenticate_user()
        url = reverse("bookings:reservation-list")
        data = {
            "tickets": [{"row": 15, "seat": 10, "performance": self.performance.id}]
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_reservation_duplicate_seat(self):
        """Test creating reservation for already booked seat fails"""
        self.authenticate_user()
        url = reverse("bookings:reservation-list")
        data = {"tickets": [{"row": 5, "seat": 10, "performance": self.performance.id}]}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_multiple_tickets_reservation(self):
        """Test creating reservation with multiple tickets"""
        self.authenticate_user()
        url = reverse("bookings:reservation-list")
        data = {
            "tickets": [
                {"row": 3, "seat": 15, "performance": self.performance.id},
                {"row": 3, "seat": 16, "performance": self.performance.id},
            ]
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        new_reservation = Reservation.objects.get(id=response.data["id"])
        self.assertEqual(new_reservation.reservation_tickets.count(), 2)

    def test_retrieve_reservation(self):
        """Test retrieving specific reservation"""
        self.authenticate_user()
        url = reverse("bookings:reservation-detail", kwargs={"pk": self.reservation.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.reservation.id)

    def test_retrieve_other_user_reservation_fails(self):
        """Test user cannot retrieve other user's reservation"""
        other_reservation = Reservation.objects.create(user=self.other_user)

        self.authenticate_user()
        url = reverse(
            "bookings:reservation-detail", kwargs={"pk": other_reservation.pk}
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_admin_retrieve_any_reservation(self):
        """Test admin can retrieve any user's reservation"""
        other_reservation = Reservation.objects.create(user=self.other_user)

        self.authenticate_admin()
        url = reverse(
            "bookings:reservation-detail", kwargs={"pk": other_reservation.pk}
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_reservation(self):
        """Test deleting reservation"""
        self.authenticate_user()
        url = reverse("bookings:reservation-detail", kwargs={"pk": self.reservation.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Reservation.objects.count(), 0)

    def test_search_reservations_by_play(self):
        """Test searching reservations by play title"""
        self.authenticate_user()
        url = reverse("bookings:reservation-list") + "?search=hamlet"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_filter_reservations(self):
        """Test filtering reservations"""
        self.authenticate_user()
        url = reverse("bookings:reservation-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class TicketViewSetTest(BaseBookingAPITest):
    def setUp(self):
        super().setUp()
        self.reservation = Reservation.objects.create(user=self.user)
        self.ticket = Ticket.objects.create(
            row=5, seat=10, performance=self.performance, reservation=self.reservation
        )

    def test_list_tickets_authenticated(self):
        """Test authenticated user can list their own tickets"""
        self.authenticate_user()
        url = reverse("bookings:ticket-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_list_tickets_unauthenticated(self):
        """Test unauthenticated user cannot list tickets"""
        url = reverse("bookings:ticket-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_retrieve_ticket(self):
        """Test retrieving specific ticket"""
        self.authenticate_user()
        url = reverse("bookings:ticket-detail", kwargs={"pk": self.ticket.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.ticket.id)
        self.assertIn("performance", response.data)

    def test_retrieve_other_user_ticket_fails(self):
        """Test user cannot retrieve other user's ticket"""
        other_reservation = Reservation.objects.create(user=self.other_user)
        other_ticket = Ticket.objects.create(
            row=6, seat=10, performance=self.performance, reservation=other_reservation
        )

        self.authenticate_user()
        url = reverse("bookings:ticket-detail", kwargs={"pk": other_ticket.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_ticket_not_allowed(self):
        """Test creating ticket directly is not allowed (ReadOnlyViewSet)"""
        self.authenticate_user()
        url = reverse("bookings:ticket-list")
        data = {
            "row": 7,
            "seat": 15,
            "performance": self.performance.id,
            "reservation": self.reservation.id,
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_ticket_not_allowed(self):
        """Test updating ticket directly is not allowed (ReadOnlyViewSet)"""
        self.authenticate_user()
        url = reverse("bookings:ticket-detail", kwargs={"pk": self.ticket.pk})
        data = {"row": 8}
        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_delete_ticket_not_allowed(self):
        """Test deleting ticket directly is not allowed (ReadOnlyViewSet)"""
        self.authenticate_user()
        url = reverse("bookings:ticket-detail", kwargs={"pk": self.ticket.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_search_tickets_by_play(self):
        """Test searching tickets by play title"""
        self.authenticate_user()
        url = reverse("bookings:ticket-list") + "?search=hamlet"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_filter_tickets(self):
        """Test filtering tickets"""
        self.authenticate_user()
        url = reverse("bookings:ticket-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
