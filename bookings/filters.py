import django_filters
from .models import Reservation, Ticket
from theatre.models import Performance


class ReservationFilter(django_filters.FilterSet):

    created_from = django_filters.DateFilter(
        field_name="created_at__date",
        lookup_expr="gte",
    )
    created_to = django_filters.DateFilter(
        field_name="created_at__date",
        lookup_expr="lte",
    )
    
    play_title = django_filters.CharFilter(
        field_name="reservation_tickets__performance__play__title",
        lookup_expr="icontains",
        distinct=True,
    )
    
    performance = django_filters.ModelChoiceFilter(
        queryset=Performance.objects.all(),
        field_name="reservation_tickets__performance",
        distinct=True,
    )

    class Meta:
        model = Reservation
        fields = ("created_from", "created_to", "play_title", "performance")


class TicketFilter(django_filters.FilterSet):

    show_date_from = django_filters.DateFilter(
        field_name="performance__show_time__date",
        lookup_expr="gte",
    )
    show_date_to = django_filters.DateFilter(
        field_name="performance__show_time__date",
        lookup_expr="lte",
    )

    class Meta:
        model = Ticket
        fields = ("show_date_from", "show_date_to")