from django.urls import path, include

from rest_framework.routers import DefaultRouter
from bookings.views import ReservationViewSet, TicketViewSet

router = DefaultRouter()
router.register("reservations", ReservationViewSet, basename="reservation")
router.register("tickets", TicketViewSet, basename="ticket")

urlpatterns = [
    path("", include(router.urls))
]

app_name = "bookings"