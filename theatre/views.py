from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet, ModelViewSet

from py_theatre_api.permissions import IsAdminOrIfAuthenticatedReadOnly
from theatre.models import Genre, Actor, TheatreHall
from theatre.serializers import GenreSerializer, ActorSerializer, TheatreHallSerializer


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
