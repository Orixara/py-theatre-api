from rest_framework.viewsets import ModelViewSet
from django.db.models import Count, F
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from theatre.filters import PlayFilter, PerformanceFilter

from py_theatre_api.permissions import IsAdminOrIfAuthenticatedReadOnly
from theatre.models import Genre, Actor, TheatreHall, Play, Performance
from theatre.serializers import (
    GenreSerializer,
    ActorSerializer,
    TheatreHallSerializer,
    PlaySerializer,
    PlayListSerializer,
    PlayDetailSerializer,
    PerformanceSerializer,
    PerformanceListSerializer,
    PerformanceDetailSerializer
)


class GenreViewSet(ModelViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly, )


class ActorViewSet(ModelViewSet):
    queryset = Actor.objects.all()
    serializer_class = ActorSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly, )


class TheatreHallViewSet(ModelViewSet):
    queryset = TheatreHall.objects.all()
    serializer_class = TheatreHallSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly, )


class PlayViewSet(ModelViewSet):
    queryset = Play.objects.all()
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly, )

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = PlayFilter
    search_fields = (
        "title",
        "description",
        "actors__first_name",
        "actors__last_name"
    )
    ordering_fields = ("title", "id")
    ordering = ("title", )

    def get_serializer_class(self):
        if self.action == "list":
            return PlayListSerializer
        if self.action == "retrieve":
            return PlayDetailSerializer
        return PlaySerializer

    def get_queryset(self):
        queryset = self.queryset
        if self.action in ["list", "retrieve"]:
            queryset = queryset.prefetch_related("actors", "genres")
        return queryset


class PerformanceViewSet(ModelViewSet):
    queryset = Performance.objects.all()
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly, )

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = PerformanceFilter
    search_fields = ("play__title", "play__description")
    ordering_fields = ("show_time", "id")
    ordering = ("show_time",)

    def get_serializer_class(self):
        if self.action == "list":
            return PerformanceListSerializer
        if self.action == "retrieve":
            return PerformanceDetailSerializer
        return PerformanceSerializer

    def get_queryset(self):
        queryset = self.queryset
        if self.action == "list":
            queryset = (
                queryset
                .select_related("play", "theatre_hall")
                .annotate(
                    tickets_available=(
                        F("theatre_hall__rows") * F("theatre_hall__seats_in_row")
                    )  - Count("tickets")
                )
                .order_by("show_time")
            )
        elif self.action == "retrieve":
            queryset = queryset.select_related(
                "play",
                "theatre_hall"
            ).prefetch_related("tickets")
        return queryset