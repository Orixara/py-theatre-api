from django.contrib import admin

from theatre.models import (
    Actor,
    Genre,
    TheatreHall,
    Performance,
    Play
)

admin.site.register(Actor)
admin.site.register(Genre)
admin.site.register(TheatreHall)
admin.site.register(Performance)
admin.site.register(Play)
