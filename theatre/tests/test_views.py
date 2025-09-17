from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken
from theatre.models import Genre, Actor, TheatreHall, Play, Performance
from datetime import datetime


User = get_user_model()


class BaseTheatreAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )
        self.admin_user = User.objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="adminpass123"
        )

    def authenticate_user(self, user=None):
        if user is None:
            user = self.user
        refresh = RefreshToken.for_user(user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')

    def authenticate_admin(self):
        self.authenticate_user(self.admin_user)


class GenreViewSetTest(BaseTheatreAPITest):
    def setUp(self):
        super().setUp()
        self.genre = Genre.objects.create(name="Drama")

    def test_list_genres_authenticated(self):
        """Test listing genres as authenticated user"""
        self.authenticate_user()
        url = reverse('theatre:genre-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_list_genres_unauthenticated(self):
        """Test listing genres as unauthenticated user"""
        url = reverse('theatre:genre-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_genre_admin(self):
        """Test creating genre as admin"""
        self.authenticate_admin()
        url = reverse('theatre:genre-list')
        data = {"name": "Comedy"}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Genre.objects.count(), 2)

    def test_create_genre_regular_user(self):
        """Test creating genre as regular user (should fail)"""
        self.authenticate_user()
        url = reverse('theatre:genre-list')
        data = {"name": "Comedy"}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_genre_admin(self):
        """Test updating genre as admin"""
        self.authenticate_admin()
        url = reverse('theatre:genre-detail', kwargs={'pk': self.genre.pk})
        data = {"name": "Updated Drama"}
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.genre.refresh_from_db()
        self.assertEqual(self.genre.name, "Updated Drama")

    def test_delete_genre_admin(self):
        """Test deleting genre as admin"""
        self.authenticate_admin()
        url = reverse('theatre:genre-detail', kwargs={'pk': self.genre.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Genre.objects.count(), 0)


class ActorViewSetTest(BaseTheatreAPITest):
    def setUp(self):
        super().setUp()
        self.actor = Actor.objects.create(first_name="John", last_name="Doe")

    def test_list_actors_authenticated(self):
        """Test listing actors as authenticated user"""
        self.authenticate_user()
        url = reverse('theatre:actor-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_create_actor_admin(self):
        """Test creating actor as admin"""
        self.authenticate_admin()
        url = reverse('theatre:actor-list')
        data = {"first_name": "Jane", "last_name": "Smith"}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Actor.objects.count(), 2)

    def test_retrieve_actor_details(self):
        """Test retrieving actor details"""
        self.authenticate_user()
        url = reverse('theatre:actor-detail', kwargs={'pk': self.actor.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['full_name'], "John Doe")


class TheatreHallViewSetTest(BaseTheatreAPITest):
    def setUp(self):
        super().setUp()
        self.hall = TheatreHall.objects.create(
            name="Main Hall",
            rows=10,
            seats_in_row=20
        )

    def test_list_halls_authenticated(self):
        """Test listing theatre halls as authenticated user"""
        self.authenticate_user()
        url = reverse('theatre:theatrehall-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_create_hall_admin(self):
        """Test creating theatre hall as admin"""
        self.authenticate_admin()
        url = reverse('theatre:theatrehall-list')
        data = {"name": "Small Hall", "rows": 5, "seats_in_row": 15}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(TheatreHall.objects.count(), 2)

    def test_retrieve_hall_capacity(self):
        """Test retrieving hall with capacity calculation"""
        self.authenticate_user()
        url = reverse('theatre:theatrehall-detail', kwargs={'pk': self.hall.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['capacity'], 200)


class PlayViewSetTest(BaseTheatreAPITest):
    def setUp(self):
        super().setUp()
        self.genre = Genre.objects.create(name="Drama")
        self.actor = Actor.objects.create(first_name="John", last_name="Doe")
        self.play = Play.objects.create(
            title="Hamlet",
            description="A famous Shakespeare play"
        )
        self.play.genres.add(self.genre)
        self.play.actors.add(self.actor)

    def test_list_plays_authenticated(self):
        """Test listing plays as authenticated user"""
        self.authenticate_user()
        url = reverse('theatre:play-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_create_play_admin(self):
        """Test creating play as admin"""
        self.authenticate_admin()
        url = reverse('theatre:play-list')
        data = {
            "title": "Romeo and Juliet",
            "description": "Another Shakespeare play",
            "genres": [self.genre.id],
            "actors": [self.actor.id]
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Play.objects.count(), 2)

    def test_retrieve_play_detail(self):
        """Test retrieving play detail with nested data"""
        self.authenticate_user()
        url = reverse('theatre:play-detail', kwargs={'pk': self.play.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('actors', response.data)
        self.assertIn('genres', response.data)

    def test_search_plays(self):
        """Test searching plays by title"""
        self.authenticate_user()
        url = reverse('theatre:play-list') + '?search=hamlet'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_filter_plays_by_genre(self):
        """Test filtering plays by genre"""
        self.authenticate_user()
        url = reverse('theatre:play-list') + f'?genres={self.genre.id}'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class PerformanceViewSetTest(BaseTheatreAPITest):
    def setUp(self):
        super().setUp()
        self.play = Play.objects.create(
            title="Hamlet",
            description="A famous Shakespeare play"
        )
        self.theatre_hall = TheatreHall.objects.create(
            name="Main Hall",
            rows=10,
            seats_in_row=20
        )
        self.performance = Performance.objects.create(
            play=self.play,
            theatre_hall=self.theatre_hall,
            show_time=datetime(2024, 12, 25, 19, 30)
        )

    def test_list_performances_authenticated(self):
        """Test listing performances as authenticated user"""
        self.authenticate_user()
        url = reverse('theatre:performance-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_create_performance_admin(self):
        """Test creating performance as admin"""
        self.authenticate_admin()
        url = reverse('theatre:performance-list')
        data = {
            "play": self.play.id,
            "theatre_hall": self.theatre_hall.id,
            "show_time": "2024-12-26T20:00:00Z"
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Performance.objects.count(), 2)

    def test_retrieve_performance_detail(self):
        """Test retrieving performance detail with nested data"""
        self.authenticate_user()
        url = reverse('theatre:performance-detail', kwargs={'pk': self.performance.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('play', response.data)
        self.assertIn('theatre_hall', response.data)

    def test_search_performances(self):
        """Test searching performances by play title"""
        self.authenticate_user()
        url = reverse('theatre:performance-list') + '?search=hamlet'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
