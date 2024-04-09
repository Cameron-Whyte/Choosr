from django.contrib.auth import authenticate
from rest_framework import serializers
from choosr.models import Movie,TVShow, Genre
from choosr.models import CustomUser
from django.contrib.auth import get_user_model

# serializer in Django REST converts complex data types into a format that can be rendered
# into JSON or other content types and also handles deserialisation.

class UserSerializer(serializers.ModelSerializer):
    watched_movies = serializers.PrimaryKeyRelatedField(many=True, queryset=Movie.objects.all())
    watched_tvshows = serializers.PrimaryKeyRelatedField(many=True, queryset=TVShow.objects.all())

    class Meta:
        model = CustomUser
        fields = ['id', 'first_name', 'last_name', 'date_of_birth', 'email', 'watched_movies', 'watched_tvshows']


#  responsible for validating the username and password provided in the request data
class UserLoginSerializer(serializers.Serializer):
    email = serializers.CharField()
    password = serializers.CharField()

    def validate(self, data):
        User = get_user_model()

        # Authenticate the user using email
        if User.objects.filter(email=data.get("email")).exists():
            user = authenticate(email=data.get("email"), password=data.get("password"))
            if user:
                return user
        raise serializers.ValidationError('Incorrect email or password. Please try again.')


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ['id', 'name']


class TVShowSerializer(serializers.ModelSerializer):
    genre_ids = GenreSerializer(many=True, read_only=True)

    class Meta:
        model = TVShow
        # id included in fields in case I later want to make more API/backend requests for more information
        fields = ['id', 'name', 'overview', 'poster_path', 'genre_ids', 'first_air_date',
                  'origin_country', 'popularity', 'number_of_seasons',
                  'episode_run_time', 'last_air_date', 'status']


class MovieSerializer(serializers.ModelSerializer):
    genre_ids = GenreSerializer(many=True, read_only=True)

    class Meta:
        model = Movie
        fields = ['id', 'title', 'overview', 'poster_path', 'genre_ids', 'release_date', 'popularity',
                  'belongs_to_collection', 'runtime', 'budget', 'revenue']

