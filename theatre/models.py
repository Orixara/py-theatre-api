from django.core.validators import MinValueValidator
from django.db import models


class Play(models.Model):
    title = models.CharField(max_length=255, unique=True)
    description = models.TextField(max_length=512)
    actors = models.ManyToManyField("Actor", related_name="plays", blank=True)
    genres = models.ManyToManyField("Genre", related_name="plays", blank=True)

    class Meta:
        verbose_name = "Play"
        verbose_name_plural = "Plays"
        ordering = ["title"]

    def __str__(self):
        return self.title


class Actor(models.Model):
    first_name = models.CharField(max_length=63)
    last_name = models.CharField(max_length=63)

    class Meta:
        verbose_name = "Actor"
        verbose_name_plural = "Actors"
        ordering = ["first_name", "last_name"]

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Genre(models.Model):
    name = models.CharField(max_length=63, unique=True)

    class Meta:
        verbose_name = "Genre"
        verbose_name_plural = "Genres"
        ordering = ["name"]

    def __str__(self):
        return self.name


class TheatreHall(models.Model):
    name = models.CharField(max_length=63, unique=True)
    rows = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    seats_in_row = models.PositiveIntegerField(validators=[MinValueValidator(1)])

    class Meta:
        verbose_name = "Theatre Hall"
        verbose_name_plural = "Theatre Halls"
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} (Rows: {self.rows}, Seats in row: {self.seats_in_row})"


class Performance(models.Model):
    play = models.ForeignKey(
        "Play",
        related_name="performances",
        on_delete=models.CASCADE
    )
    theatre_hall = models.ForeignKey(
        "TheatreHall",
        related_name="hall_performances",
        on_delete=models.CASCADE
    )
    show_time = models.DateTimeField(db_index=True)

    class Meta:
        ordering = ["-show_time"]

    def __str__(self):
        return f"Performance {self.id} - {self.show_time}"

