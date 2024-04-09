from datetime import datetime, date
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from choosr.models import Movie, Genre, WatchedMovie, CustomUser

# test for the questionnaire / advanced questionnaire for movies
# also an integration test as we test the view, the database, and response format
# creates 8 movie  objects and then applies answers as filters to return them correctly
class MovieListViewTest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        horror_genre = Genre.objects.create(id="27")
        # create 8  movies
        for i in range(8):
            Movie.objects.create(
                id=i,
                title=f"Movie {i}",
                overview="This is an overview",
                release_date="2017-01-01",
                popularity=80.0,
                poster_path="/xy{i}",
                belongs_to_collection=f"Movie Collection {i}",
                runtime=110,
                budget=1000000,
                revenue=2000000,
            ).genres.add(horror_genre)

        Movie.objects.create(
            id=10,
            title="Movie 10",
            overview="This is an overview",
            release_date="2019-01-01",
            popularity=80.0,
            poster_path="/xy{i}",
            belongs_to_collection="Movie Collection 10",
            runtime=60,
            budget=1000000,
            revenue=2000000,
        ).genres.add(horror_genre)

    def setUp(self):
        self.client = APIClient()

    # map answers function to mimic frontend questionnaire.js
    def map_answers(self, answers):
        return {
            'content_type': {'Film': 'movie', 'TV': 'tv'}[answers['content_type']],
            'genre': answers['genre'],
            'mainstream': {'Yes': '>10', 'No': '<=10'}[answers['mainstream']],
            'period': {
                'Current': 'Current',
                '2010s': '2010',
                '2000s': '2000',
                '1990s': '1990',
                '1980s': '1980',
                '1970s or earlier': '<1970',
            }[answers['period']],
            'length': answers['length'],
            'collection': None if answers['collection'] == 'Indifferent' else answers['collection'],
            'budget': None if answers['budget'] == 'Indifferent' else answers['budget'],
            'revenue': None if answers['revenue'] == 'Indifferent' else answers['revenue'],
        }

    # provide answers as a user would
    def test_movie_list_view(self):
        answers = {
            'content_type': 'Film',
            'genre': 'Horror',
            'mainstream': 'Yes',
            'period': '2010s',
            'length': '90mins',
            'collection': 'Yes',
            'budget': 'No',
            'revenue': 'No'
        }
        mapped_answers = self.map_answers(answers)
        backend_url = f"http://localhost:8000/{mapped_answers['content_type']}/"

        response = self.client.get(backend_url, mapped_answers)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 8)  # expect 8 movies
        response_data = response.data
        for i in range(8):
            expected_movie_title = 'Movie ' + str(i)
            actual_movie_title = response_data[i]['title']
            self.assertEqual(actual_movie_title, expected_movie_title) # ensure the expected movies are in the response

    def test_remove_filters_function(self):
        answers = {
            'content_type': 'Film',
            'genre': 'Horror',
            'mainstream': 'Yes',
            'period': '2010s',
            'length': '60mins', # causes filters to be removed
            'collection': 'Yes',
            'budget': 'No',
            'revenue': 'No'
        }
        mapped_answers = self.map_answers(answers)
        backend_url = f"http://localhost:8000/{mapped_answers['content_type']}/"
        response = self.client.get(backend_url, mapped_answers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 8) # expect 8 movies after filters are removed

    # test exclusion works as expected
    def test_exclude_ids(self):
        answers = {
            'content_type': 'Film',
            'genre': 'Horror',
            'mainstream': 'Yes',
            'period': '2010s',
            'length': '90mins',
            'collection': 'Yes',
            'budget': 'No',
            'revenue': 'No'
        }
        exclude_ids = "3"
        mapped_answers = self.map_answers(answers)
        mapped_answers['exclude'] = exclude_ids
        backend_url = f"http://localhost:8000/{mapped_answers['content_type']}/"
        response = self.client.get(backend_url, mapped_answers)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 7)  # expect 7 movies since 1 is excluded
        excluded_movie_titles = "Movie 3"
        response_data = response.data
        for show in response_data:
            self.assertNotIn(show['title'], excluded_movie_titles)  # assert that excluded movies are not in the response


class BaseWatchedMovieTest(APITestCase):
    def setUp(self):
        horror_genre = Genre.objects.create(id="27")
        self.movie = Movie.objects.create(
            id=1,
            title="Movie 1",
            overview="This is an overview",
            release_date="2019-01-01",
            popularity=80.0,
            poster_path="/xy1",
            belongs_to_collection="Movie Collection 10",
            runtime=60,
            budget=1000000,
            revenue=2000000,
        )
        self.movie.genres.add(horror_genre)
        # create a user to add / remove the show
        self.user = CustomUser.objects.create_user(username='testuser', email='test@example.com',
                                                   date_of_birth='2000-01-01', password='thisissecure')
        self.client = APIClient()


class AddWatchedMovieTest(BaseWatchedMovieTest):

    def setUp(self):
        super().setUp()
        self.url = reverse('add-watched-movie')

    def test_add_watched_movie_authenticated(self):
        # force authenticates a user
        self.client.force_authenticate(user=self.user)
        # sends the id to be added
        response = self.client.post(self.url, {'movie_id': self.movie.id})
        # status 200 means successful add
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # users watched movies should have a total of 1 now
        self.assertEqual(WatchedMovie.objects.filter(user=self.user, movie__id=self.movie.id).count(), 1)

    def test_add_watched_movie_unauthenticated(self):
        # without authentication the request should fail
        response = self.client.post(self.url, {'movie_id': self.movie.id})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


# same as add except there should be no movies after the operation
class RemoveWatchedMovieTest(BaseWatchedMovieTest):
    def setUp(self):
        super().setUp()
        WatchedMovie.objects.create(user=self.user, movie=self.movie)
        self.url = reverse('remove-watched-movie')

    def test_remove_watched_movie_authenticated(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.url, {'movie_id': self.movie.id})
        self.assertEqual(response.status_code,
                         status.HTTP_204_NO_CONTENT)

    def test_remove_watched_movie_unauthenticated(self):
        response = self.client.post(self.url, {'movie_id': self.movie.id})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class DualRecommendMovieTest(APITestCase):

    def setUp(self):
        self.client = APIClient()
        # Create users
        self.user1 = CustomUser.objects.create(email='user1@example.com', date_of_birth='1990-01-01',
                                               password='securetestpass')
        self.user2 = CustomUser.objects.create(email='user2@example.com', date_of_birth='1990-01-01',
                                               password='securetestpass')
        # Create genres
        self.genre1 = Genre.objects.create(id="35")
        self.genre2 = Genre.objects.create(id='18')
        # Create movies
        self.movie1 = Movie.objects.create(
            id=1,
            title="Movie 1",
            overview="This is an overview",
            release_date="2019-01-01",
            popularity=80.0,
            poster_path="/xy1",
            belongs_to_collection="Movie Collection 1",
            runtime=60,
            budget=1000000,
            revenue=2000000,
        )
        self.movie1.genres.add(self.genre1)

        self.movie2 = Movie.objects.create(
            id=2,
            title="Movie 2",
            overview="This is an overview",
            release_date="2010-01-01",
            popularity=45.0,
            poster_path="/xy1",
            belongs_to_collection="Movie Collection 2",
            runtime=90,
            budget=100000000,
            revenue=200000000,
        )
        self.movie2.genres.add(self.genre2)
        # Create Watched movies
        WatchedMovie.objects.create(user=self.user1, movie=self.movie1)
        WatchedMovie.objects.create(user=self.user2, movie=self.movie2)

        genres = [self.genre1, self.genre2]
        # creating 16 movies, alternating between odd and even to mix values
        for i in range(3, 19):  # IDs start from 3 since 1 and 2 are already used
            movie = Movie.objects.create(
                id=i,
                title=f"Movie {i}",
                overview="This is an overview",
                release_date="2018-01-01" if i % 2 == 0 else "2014-01-01",
                popularity=30.0 if i % 2 == 0 else 60.0,
                belongs_to_collection=f"Movie Collection {i}",
                poster_path=f"/xy{i}",
                runtime=120 if i % 2 == 0 else 90,
                budget=1000000 if i % 2 == 0 else 100000000,
                revenue=2000000 if i % 2 == 0 else 200000000,
            )
            movie.genres.add(genres[i % 2])

    def test_get_recommendations(self):
        client = APIClient()
        client.force_authenticate(user=self.user1)
        url = reverse('dual-recommend-movie', args=[self.user1.email, self.user2.email])
        response = client.get(url)
        self.assertEqual(response.status_code, 200)  # Check the response is successful

        # Ensure the watched movies are not in the recommendations
        watched_movie_ids = [self.movie1.id, self.movie2.id]
        recommended_movie_ids = [movie['id'] for movie in response.data]
        for watched_movie_id in watched_movie_ids:
            self.assertNotIn(watched_movie_id, recommended_movie_ids) # watch list items should not be returned

        self.assertEqual(len(response.data), 8) # only 8 items should be returned at a time

        # Get the recommended movies from the response
        recommended_movies = Movie.objects.filter(id__in=[movie['id'] for movie in response.data])

        # Define the set of genres associated with user1 and user2
        user_genres = {self.genre1.id, self.genre2.id}

        # Iterate through the recommended movies and perform assertions
        for movie in recommended_movies:
            movie_genres = {genre.id for genre in movie.genres.all()}
            # Check if at least one of the user genres is present in the recommended movies
            self.assertTrue(user_genres.intersection(movie_genres))

        for movie in response.data:
            # ensure the attributes are in the correct range
            air_date = datetime.strptime(movie['release_date'], '%Y-%m-%d').date()
            self.assertGreaterEqual(air_date, date(2010, 1, 1))
            self.assertLessEqual(air_date, date(2019, 1, 1))
            self.assertIn(movie['runtime'], [60, 90, 120])
            self.assertIsNotNone(movie.get('belongs_to_collection'))
            self.assertIn(movie['budget'], [1000000, 100000000])
            self.assertIn(movie['revenue'], [2000000, 200000000])

