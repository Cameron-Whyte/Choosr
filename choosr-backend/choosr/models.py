from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models

# custom user manager used to support Abstract User
# https://stackoverflow.com/questions/66577984/migrate-from-standard-user-to-abstract-custom-user-in-django
class CustomUserManager(BaseUserManager):
    def create_user(self, email, date_of_birth, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, date_of_birth=date_of_birth, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, date_of_birth, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        return self.create_user(email, date_of_birth, password, **extra_fields)


class CustomUser(AbstractUser):
    # doing this stops username being a blank which stops new accounts from being created
    username = models.CharField(max_length=150, unique=False, null=True, blank=True)
    email = models.EmailField(unique=True)
    date_of_birth = models.DateField(null=True, blank=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['date_of_birth']
    objects = CustomUserManager()


class Genre(models.Model):
    id = models.CharField(max_length=16, primary_key=True)


class Movie(models.Model):
    id = models.IntegerField(primary_key=True)
    title = models.CharField(max_length=200)
    overview = models.TextField()
    genres = models.ManyToManyField(Genre)
    release_date = models.DateField()
    popularity = models.FloatField()
    poster_path = models.CharField(max_length=500, null=True, blank=True)
    belongs_to_collection = models.CharField(max_length=200, null=True, blank=True)
    runtime = models.IntegerField(null=True, blank=True)
    budget = models.BigIntegerField(null=True, blank=True)
    revenue = models.BigIntegerField(null=True, blank=True)


    def __str__(self):
        return f"{self.id} - {self.title}"

class TVShow(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=200)
    overview = models.TextField()
    genres = models.ManyToManyField(Genre)
    first_air_date = models.DateField()
    origin_country = models.TextField()
    popularity = models.FloatField()
    poster_path = models.CharField(max_length=500, null=True, blank=True)
    number_of_seasons = models.IntegerField(null=True, blank=True)
    episode_run_time = models.IntegerField(null=True, blank=True)
    last_air_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.id} - {self.name}"


class WatchedMovie(models.Model):
    user = models.ForeignKey(CustomUser, related_name='watched_movies', on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)


class WatchedTVShow(models.Model):
    user = models.ForeignKey(CustomUser, related_name='watched_tvshows', on_delete=models.CASCADE)
    tvshow = models.ForeignKey(TVShow, on_delete=models.CASCADE)


# models for timing tests, would be removed in operational application
class TimeTakenUnregistered(models.Model):
    time_taken = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)


class TimeTakenRegistered(models.Model):
    time_taken = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
