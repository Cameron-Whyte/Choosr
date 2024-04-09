from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from choosr.models import Genre, CustomUser, Movie, TVShow, WatchedMovie, \
    WatchedTVShow


class TopPicksTests(APITestCase):

    def setUp(self):
        self.client = APIClient()

        # Create genres
        comedy_genre = Genre.objects.create(id="35")
        horror_genre = Genre.objects.create(id="27")

        # Create 10 movies with all attributes
        self.movies = []
        for i in range(10):
            movie = Movie.objects.create(
                id=i,
                title=f"Movie {i}",
                overview="This is an overview",
                release_date="2017-01-01",
                popularity=80.0,
                poster_path=f"/xy{i}",
                belongs_to_collection=f"Movie Collection {i}",
                runtime=110,
                budget=1000000,
                revenue=2000000
            )
            movie.genres.add(horror_genre)
            self.movies.append(movie)

        # Create 10 TV shows with all attributes
        self.tv_shows = []
        for i in range(10):
            tv_show = TVShow.objects.create(
                id=i,
                name=f"Show {i}",
                overview="This is an overview",
                first_air_date="2022-01-01",
                origin_country="US",
                popularity=5.5,
                status="Running",
                poster_path=f"/xy{i}",
                number_of_seasons=3,
                episode_run_time=30,
                last_air_date="2022-08-01",
            )
            tv_show.genres.add(comedy_genre)
            self.tv_shows.append(tv_show)

        # Create 6 users
        self.users = [CustomUser.objects.create(email=f"user{i}@example.com", date_of_birth='1990-01-01',
                                                password='securetestpass') for i in range(1, 7)]

        # Add 6 movies and TV shows to 4 users
        for user in self.users[:4]:
            for movie in self.movies[:6]:
                WatchedMovie.objects.create(user=user, movie=movie)
            for tv_show in self.tv_shows[:6]:
                WatchedTVShow.objects.create(user=user, tvshow=tv_show)

        # Add the other 4 movies and TV shows to the remaining 2 users
        for user in self.users[4:]:
            for movie in self.movies[6:]:
                WatchedMovie.objects.create(user=user, movie=movie)
            for tv_show in self.tv_shows[6:]:
                WatchedTVShow.objects.create(user=user, tvshow=tv_show)

    def test_top_picks(self):
        url = reverse('top-picks')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Ensure the top picks are those added to 4 users
        expected_top_movie_ids = [movie.id for movie in self.movies[:6]]
        returned_movie_ids = [movie['id'] for movie in response.data['movies']]
        self.assertEqual(set(expected_top_movie_ids), set(returned_movie_ids))

        expected_top_tv_show_ids = [tv_show.id for tv_show in self.tv_shows[:6]]
        returned_tv_show_ids = [tv_show['id'] for tv_show in response.data['tv_shows']]
        self.assertEqual(set(expected_top_tv_show_ids), set(returned_tv_show_ids))

        # Remove 1 movie and 1 TV show from each user, and add a different one
        for user in self.users[:4]:
            WatchedMovie.objects.filter(user=user, movie=self.movies[0]).delete()
            WatchedMovie.objects.create(user=user, movie=self.movies[6])

            WatchedTVShow.objects.filter(user=user, tvshow=self.tv_shows[0]).delete()
            WatchedTVShow.objects.create(user=user, tvshow=self.tv_shows[6])

        # Get the top picks and assert
        response = self.client.get(url)

        new_top_movie_ids = [movie.id for movie in self.movies[1:7]]  # remove the first and include the seventh
        new_returned_movie_ids = [movie['id'] for movie in response.data['movies']]
        self.assertEqual(set(new_top_movie_ids), set(new_returned_movie_ids))

        new_top_tv_show_ids = [tv_show.id for tv_show in self.tv_shows[1:7]]  # remove the first and include the seventh
        new_returned_tv_show_ids = [tv_show['id'] for tv_show in response.data['tv_shows']]
        self.assertEqual(set(new_top_tv_show_ids), set(new_returned_tv_show_ids))
