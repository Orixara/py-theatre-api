import django_filters

from theatre.models import Performance, Play, Genre, Actor, TheatreHall


class PlayFilter(django_filters.FilterSet):
    title = django_filters.CharFilter(lookup_expr="icontains")
    actors = django_filters.ModelMultipleChoiceFilter(
        queryset=Actor.objects.all(),
        field_name="actors__id",
        to_field_name="id"
    )
    genres = django_filters.ModelMultipleChoiceFilter(
        queryset=Genre.objects.all(),
        field_name="genres__id",
        to_field_name="id"
    )

    class Meta:
        model = Play
        fields = ("title", "actors", "genres")


class PerformanceFilter(django_filters.FilterSet):
    date_from = django_filters.DateFilter(
        field_name="show_time__date",
        lookup_expr="gte",
    )
    date_to = django_filters.DateFilter(
        field_name="show_time__date",
        lookup_expr="lte",
    )
    time_from = django_filters.TimeFilter(
        field_name="show_time__time",
        lookup_expr="gte",
    )
    time_to = django_filters.TimeFilter(
        field_name="show_time__time",
        lookup_expr="lte",
    )

    play_genres = django_filters.ModelMultipleChoiceFilter(
        queryset=Genre.objects.all(),
        field_name="play__genres__id",
        to_field_name="id",
    )

    play_actors = django_filters.ModelMultipleChoiceFilter(
        queryset=Actor.objects.all(),
        field_name="play__actors__id",
        to_field_name="id",
    )

    play_title = django_filters.CharFilter(
        field_name="play__title",
        lookup_expr="icontains",
    )

    theatre_hall = django_filters.ModelChoiceFilter(
        queryset=TheatreHall.objects.all()
    )

    has_available_tickets = django_filters.BooleanFilter(
        method="filter_available_tickets"
    )

    def filter_available_tickets(self, queryset, name, value):
        if value:
            return queryset.filter(tickets_available__gt=0)
        return queryset

    class Meta:
        model = Performance
        fields = [
            "date_from", "date_to", "time_from", "time_to",
            "play_genres", "play_actors", "play_title",
            "theatre_hall", "has_available_tickets",
        ]