from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.contrib.auth import get_user_model

from theatre.models import Performance


User = get_user_model()


class Reservation(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, related_name="reservations", on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Reservation"
        verbose_name_plural = "Reservations"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Reservation - ({self.id}: {self.created_at})"


class Ticket(models.Model):
    row = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    seat = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    performance = models.ForeignKey(
        Performance,
        related_name="tickets",
        on_delete=models.CASCADE,
    )
    reservation = models.ForeignKey(
        "Reservation",
        related_name="reservation_tickets",
        on_delete=models.CASCADE
    )

    @staticmethod
    def validate_tickets(row, seat, theatre_hall, error_to_raise):
        for ticket_attr_value, ticket_attr_name, theatre_hall_attr_name in [
            (row, "row", "rows"),
            (seat, "seat", "seats_in_row")
        ]:
            count_attrs = getattr(theatre_hall, theatre_hall_attr_name)
            if not (1 <= ticket_attr_value <= count_attrs):
                raise error_to_raise(
                    {
                        ticket_attr_name: f"{ticket_attr_name} "
                        f"number must be in available range: "
                        f"(1, {theatre_hall_attr_name}): "
                        f"(1, {count_attrs})"
                    }
                )

    def clean(self):
        Ticket.validate_tickets(
            self.row,
            self.seat,
            self.performance.theatre_hall,
            ValidationError,
        )
        
        existing_ticket = Ticket.objects.filter(
            performance=self.performance,
            row=self.row,
            seat=self.seat
        ).exclude(pk=self.pk)
        
        if existing_ticket.exists():
            raise ValidationError(
                {"__all__": "This seat is already booked"}
            )

    def save(
            self,
            *args,
            force_insert=False,
            force_update=False,
            using=None,
            update_fields=None,
    ):
        self.full_clean()
        return super(Ticket, self).save(
            force_insert, force_update, using, update_fields
        )

    class Meta:
        verbose_name = "Ticket"
        verbose_name_plural = "Tickets"
        ordering = ("row", "seat")

    def __str__(self):
        return (
            f"{str(self.performance)} (row: {self.row}, seat: {self.seat})"
        )