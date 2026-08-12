import factory
from django.utils import timezone

from game_monitor.models import Game, UserPhone


class UserPhoneFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = UserPhone

    phone_number = factory.Sequence(lambda n: f"+1{5550000000 + n}")


class GameFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Game

    title = factory.Faker("sentence", nb_words=4)
    date = factory.LazyFunction(timezone.now)
    home_team = factory.Faker("city")
    away_team = factory.Faker("city")
    home_team_score = factory.Faker("random_int", min=80, max=120)
    away_team_score = factory.Faker("random_int", min=80, max=120)
    game_clock = factory.Faker("time")
    period = factory.Faker("random_int", min=1, max=4)
