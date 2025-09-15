from django.contrib import admin

from bookings.models import Reservation, Ticket


admin.site.register(Reservation)
admin.site.register(Ticket)