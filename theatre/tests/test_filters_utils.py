from django.test import TestCase
from django.contrib.auth import get_user_model
from theatre.models import Genre, Actor, TheatreHall, Play, Performance
from theatre.filters import PlayFilter, PerformanceFilter
from theatre.utils import play_image_file_path
from datetime import datetime



User = get_user_model()


class PlayFilterTest(TestCase):
    def setUp(self):
        self.genre1 = Genre.objects.create(name="Drama")
        self.genre2 = Genre.objects.create(name="Comedy")
        self.actor1 = Actor.objects.create(first_name="John", last_name="Doe")
        self.actor2 = Actor.objects.create(first_name="Jane", last_name="Smith")
        
        self.play1 = Play.objects.create(
            title="Hamlet",
            description="A famous Shakespeare play"
        )
        self.play1.genres.add(self.genre1)
        self.play1.actors.add(self.actor1)
        
        self.play2 = Play.objects.create(
            title="Comedy Night",
            description="A funny play"
        )
        self.play2.genres.add(self.genre2)
        self.play2.actors.add(self.actor2)

    def test_filter_play_by_title_icontains(self):
        """Test filtering plays by title (case insensitive)"""
        filter_data = {"title": "hamlet"}
        play_filter = PlayFilter(data=filter_data, queryset=Play.objects.all())
        self.assertTrue(play_filter.is_valid())
        filtered_plays = play_filter.qs
        self.assertEqual(filtered_plays.count(), 1)
        self.assertEqual(filtered_plays.first(), self.play1)

    def test_filter_play_by_genre(self):
        """Test filtering plays by genre"""
        filter_data = {"genres": [self.genre1.id]}
        play_filter = PlayFilter(data=filter_data, queryset=Play.objects.all())
        self.assertTrue(play_filter.is_valid())
        filtered_plays = play_filter.qs
        self.assertEqual(filtered_plays.count(), 1)
        self.assertEqual(filtered_plays.first(), self.play1)

    def test_filter_play_by_multiple_genres(self):
        """Test filtering plays by multiple genres"""
        filter_data = {"genres": [self.genre1.id, self.genre2.id]}
        play_filter = PlayFilter(data=filter_data, queryset=Play.objects.all())
        self.assertTrue(play_filter.is_valid())
        filtered_plays = play_filter.qs
        self.assertEqual(filtered_plays.count(), 2)

    def test_filter_play_by_actor(self):
        """Test filtering plays by actor"""
        filter_data = {"actors": [self.actor1.id]}
        play_filter = PlayFilter(data=filter_data, queryset=Play.objects.all())
        self.assertTrue(play_filter.is_valid())
        filtered_plays = play_filter.qs
        self.assertEqual(filtered_plays.count(), 1)
        self.assertEqual(filtered_plays.first(), self.play1)

    def test_filter_play_by_multiple_actors(self):
        """Test filtering plays by multiple actors"""
        filter_data = {"actors": [self.actor1.id, self.actor2.id]}
        play_filter = PlayFilter(data=filter_data, queryset=Play.objects.all())
        self.assertTrue(play_filter.is_valid())
        filtered_plays = play_filter.qs
        self.assertEqual(filtered_plays.count(), 2)

    def test_filter_play_combined_filters(self):
        """Test filtering plays with combined filters"""
        filter_data = {
            "title": "hamlet",
            "genres": [self.genre1.id],
            "actors": [self.actor1.id]
        }
        play_filter = PlayFilter(data=filter_data, queryset=Play.objects.all())
        self.assertTrue(play_filter.is_valid())
        filtered_plays = play_filter.qs
        self.assertEqual(filtered_plays.count(), 1)
        self.assertEqual(filtered_plays.first(), self.play1)

    def test_filter_play_no_matches(self):
        """Test filtering plays with no matches"""
        filter_data = {"title": "nonexistent"}
        play_filter = PlayFilter(data=filter_data, queryset=Play.objects.all())
        self.assertTrue(play_filter.is_valid())
        filtered_plays = play_filter.qs
        self.assertEqual(filtered_plays.count(), 0)


class PerformanceFilterTest(TestCase):
    def setUp(self):
        self.genre1 = Genre.objects.create(name="Drama")
        self.actor1 = Actor.objects.create(first_name="John", last_name="Doe")
        self.theatre_hall1 = TheatreHall.objects.create(
            name="Main Hall", rows=10, seats_in_row=20
        )
        self.theatre_hall2 = TheatreHall.objects.create(
            name="Small Hall", rows=5, seats_in_row=15
        )
        
        self.play1 = Play.objects.create(
            title="Hamlet", description="Shakespeare play"
        )
        self.play1.genres.add(self.genre1)
        self.play1.actors.add(self.actor1)
        
        self.performance1 = Performance.objects.create(
            play=self.play1,
            theatre_hall=self.theatre_hall1,
            show_time=datetime(2024, 12, 25, 19, 30)
        )
        self.performance2 = Performance.objects.create(
            play=self.play1,
            theatre_hall=self.theatre_hall2,
            show_time=datetime(2024, 12, 26, 14, 0)
        )

    def test_filter_performance_by_date_from(self):
        """Test filtering performances from specific date"""
        filter_data = {"date_from": "2024-12-25"}
        perf_filter = PerformanceFilter(data=filter_data, queryset=Performance.objects.all())
        self.assertTrue(perf_filter.is_valid())
        filtered_performances = perf_filter.qs
        self.assertEqual(filtered_performances.count(), 2)

    def test_filter_performance_by_date_to(self):
        """Test filtering performances to specific date"""
        filter_data = {"date_to": "2024-12-25"}
        perf_filter = PerformanceFilter(data=filter_data, queryset=Performance.objects.all())
        self.assertTrue(perf_filter.is_valid())
        filtered_performances = perf_filter.qs
        self.assertEqual(filtered_performances.count(), 1)
        self.assertEqual(filtered_performances.first(), self.performance1)

    def test_filter_performance_by_date_range(self):
        """Test filtering performances by date range"""
        filter_data = {
            "date_from": "2024-12-25",
            "date_to": "2024-12-26"
        }
        perf_filter = PerformanceFilter(data=filter_data, queryset=Performance.objects.all())
        self.assertTrue(perf_filter.is_valid())
        filtered_performances = perf_filter.qs
        self.assertEqual(filtered_performances.count(), 2)

    def test_filter_performance_by_time_from(self):
        """Test filtering performances from specific time"""
        filter_data = {"time_from": "15:00"}
        perf_filter = PerformanceFilter(data=filter_data, queryset=Performance.objects.all())
        self.assertTrue(perf_filter.is_valid())
        filtered_performances = perf_filter.qs
        self.assertEqual(filtered_performances.count(), 1)
        self.assertEqual(filtered_performances.first(), self.performance1)

    def test_filter_performance_by_time_to(self):
        """Test filtering performances to specific time"""
        filter_data = {"time_to": "15:00"}
        perf_filter = PerformanceFilter(data=filter_data, queryset=Performance.objects.all())
        self.assertTrue(perf_filter.is_valid())
        filtered_performances = perf_filter.qs
        self.assertEqual(filtered_performances.count(), 1)
        self.assertEqual(filtered_performances.first(), self.performance2)

    def test_filter_performance_by_play_title(self):
        """Test filtering performances by play title"""
        filter_data = {"play_title": "hamlet"}
        perf_filter = PerformanceFilter(data=filter_data, queryset=Performance.objects.all())
        self.assertTrue(perf_filter.is_valid())
        filtered_performances = perf_filter.qs
        self.assertEqual(filtered_performances.count(), 2)

    def test_filter_performance_by_theatre_hall(self):
        """Test filtering performances by theatre hall"""
        filter_data = {"theatre_hall": self.theatre_hall1.id}
        perf_filter = PerformanceFilter(data=filter_data, queryset=Performance.objects.all())
        self.assertTrue(perf_filter.is_valid())
        filtered_performances = perf_filter.qs
        self.assertEqual(filtered_performances.count(), 1)
        self.assertEqual(filtered_performances.first(), self.performance1)

    def test_filter_performance_by_play_genres(self):
        """Test filtering performances by play genres"""
        filter_data = {"play_genres": [self.genre1.id]}
        perf_filter = PerformanceFilter(data=filter_data, queryset=Performance.objects.all())
        self.assertTrue(perf_filter.is_valid())
        filtered_performances = perf_filter.qs
        self.assertEqual(filtered_performances.count(), 2)

    def test_filter_performance_by_play_actors(self):
        """Test filtering performances by play actors"""
        filter_data = {"play_actors": [self.actor1.id]}
        perf_filter = PerformanceFilter(data=filter_data, queryset=Performance.objects.all())
        self.assertTrue(perf_filter.is_valid())
        filtered_performances = perf_filter.qs
        self.assertEqual(filtered_performances.count(), 2)

    def test_filter_performance_has_available_tickets_method(self):
        """Test custom filter method for available tickets"""
        from django.db.models import Value
        from django.db.models.fields import IntegerField
        
        queryset = Performance.objects.annotate(
            tickets_available=Value(10, output_field=IntegerField())
        )
        
        filter_data = {"has_available_tickets": True}
        perf_filter = PerformanceFilter(data=filter_data, queryset=queryset)
        self.assertTrue(perf_filter.is_valid())



class TheatreUtilsTest(TestCase):
    def test_play_image_file_path(self):
        """Test play image file path generation"""
        play = Play(title="Test Play")
        filename = "test_image.jpg"
        
        result_path = play_image_file_path(play, filename)
        
        self.assertIn("test-play", result_path)
        self.assertIn("-", result_path)
        self.assertIn(".jpg", result_path)
        self.assertIn("uploads/plays/", result_path)

    def test_play_image_file_path_with_special_characters(self):
        """Test file path generation with special characters in title"""
        play = Play(title="Test Play: The Special Edition!")
        filename = "image.png"
        
        result_path = play_image_file_path(play, filename)
        
        self.assertIn("test-play-the-special-edition", result_path)
        self.assertIn(".png", result_path)

    def test_play_image_file_path_uniqueness(self):
        """Test that generated paths are unique"""
        play = Play(title="Same Title")
        filename = "same.jpg"
        
        path1 = play_image_file_path(play, filename)
        path2 = play_image_file_path(play, filename)
        
        self.assertNotEqual(path1, path2)
        for path in [path1, path2]:
            self.assertIn("same-title", path)
            self.assertIn(".jpg", path)
            self.assertIn("uploads/plays/", path)

    def test_play_image_file_path_different_extensions(self):
        """Test file path generation with different extensions"""
        play = Play(title="Test")
        
        extensions = [".jpg", ".png", ".gif", ".webp"]
        paths = []
        
        for ext in extensions:
            path = play_image_file_path(play, f"image{ext}")
            self.assertIn(ext, path)
            paths.append(path)
        
        self.assertEqual(len(paths), len(set(paths)))

    def test_play_image_file_path_no_extension(self):
        """Test file path generation with no extension"""
        play = Play(title="Test Play")
        filename = "noextension"
        
        result_path = play_image_file_path(play, filename)
        
        self.assertIn("test-play", result_path)
        self.assertNotIn(".", result_path.split("-")[-1])
