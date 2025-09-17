from django.test import TestCase
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
)
from datetime import datetime


class GenreSerializerTest(TestCase):
    def test_genre_serializer_valid(self):
        """Test valid genre serialization"""
        data = {"name": "Drama"}
        serializer = GenreSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        genre = serializer.save()
        self.assertEqual(genre.name, "Drama")

    def test_genre_serializer_output(self):
        """Test genre serializer output"""
        genre = Genre.objects.create(name="Comedy")
        serializer = GenreSerializer(genre)
        self.assertEqual(serializer.data["name"], "Comedy")
        self.assertIn("id", serializer.data)


class ActorSerializerTest(TestCase):
    def test_actor_serializer_valid(self):
        """Test valid actor serialization"""
        data = {
            "first_name": "John",
            "last_name": "Doe"
        }
        serializer = ActorSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        actor = serializer.save()
        self.assertEqual(actor.first_name, "John")
        self.assertEqual(actor.last_name, "Doe")

    def test_actor_serializer_output(self):
        """Test actor serializer output includes full_name"""
        actor = Actor.objects.create(first_name="Jane", last_name="Smith")
        serializer = ActorSerializer(actor)
        self.assertEqual(serializer.data["full_name"], "Jane Smith")
        self.assertIn("id", serializer.data)


class TheatreHallSerializerTest(TestCase):
    def test_theatre_hall_serializer_valid(self):
        """Test valid theatre hall serialization"""
        data = {
            "name": "Main Hall",
            "rows": 10,
            "seats_in_row": 20
        }
        serializer = TheatreHallSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        hall = serializer.save()
        self.assertEqual(hall.name, "Main Hall")
        self.assertEqual(hall.capacity, 200)

    def test_theatre_hall_serializer_output(self):
        """Test theatre hall serializer output includes capacity"""
        hall = TheatreHall.objects.create(name="Small Hall", rows=5, seats_in_row=15)
        serializer = TheatreHallSerializer(hall)
        self.assertEqual(serializer.data["capacity"], 75)
        self.assertIn("id", serializer.data)


class PlaySerializerTest(TestCase):
    def setUp(self):
        self.genre = Genre.objects.create(name="Drama")
        self.actor = Actor.objects.create(first_name="John", last_name="Doe")

    def test_play_serializer_valid(self):
        """Test valid play serialization"""
        data = {
            "title": "Hamlet",
            "description": "A famous Shakespeare play",
            "actors": [self.actor.id],
            "genres": [self.genre.id]
        }
        serializer = PlaySerializer(data=data)
        self.assertTrue(serializer.is_valid())
        play = serializer.save()
        self.assertEqual(play.title, "Hamlet")

    def test_play_list_serializer(self):
        """Test play list serializer output"""
        play = Play.objects.create(
            title="Romeo and Juliet",
            description="Shakespeare play"
        )
        play.actors.add(self.actor)
        play.genres.add(self.genre)
        
        serializer = PlayListSerializer(play)
        self.assertIn("actors", serializer.data)
        self.assertIn("genres", serializer.data)
        self.assertEqual(serializer.data["actors"], ["John Doe"])
        self.assertEqual(serializer.data["genres"], ["Drama"])

    def test_play_detail_serializer(self):
        """Test play detail serializer with nested objects"""
        play = Play.objects.create(
            title="Macbeth",
            description="Shakespeare tragedy"
        )
        play.actors.add(self.actor)
        play.genres.add(self.genre)
        
        serializer = PlayDetailSerializer(play)
        self.assertIsInstance(serializer.data["actors"], list)
        self.assertIsInstance(serializer.data["genres"], list)
        self.assertEqual(len(serializer.data["actors"]), 1)
        self.assertEqual(len(serializer.data["genres"]), 1)


class PerformanceSerializerTest(TestCase):
    def setUp(self):
        self.play = Play.objects.create(
            title="Hamlet",
            description="A famous Shakespeare play"
        )
        self.theatre_hall = TheatreHall.objects.create(
            name="Main Hall",
            rows=10,
            seats_in_row=20
        )

    def test_performance_serializer_valid(self):
        """Test valid performance serialization"""
        show_time = datetime(2024, 12, 25, 19, 30)
        data = {
            "play": self.play.id,
            "theatre_hall": self.theatre_hall.id,
            "show_time": show_time.isoformat()
        }
        serializer = PerformanceSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        performance = serializer.save()
        self.assertEqual(performance.play, self.play)

    def test_performance_list_serializer(self):
        """Test performance list serializer with related data"""
        show_time = datetime(2024, 12, 25, 19, 30)
        performance = Performance.objects.create(
            play=self.play,
            theatre_hall=self.theatre_hall,
            show_time=show_time
        )
        
        performance.tickets_available = 200
        
        serializer = PerformanceListSerializer(performance)
        self.assertEqual(serializer.data["play_title"], "Hamlet")
        self.assertEqual(serializer.data["theatre_hall_name"], "Main Hall")
        self.assertEqual(serializer.data["theatre_hall_capacity"], 200)
