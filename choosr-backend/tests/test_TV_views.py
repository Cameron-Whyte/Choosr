from datetime import datetime, date
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from choosr.models import TVShow, Genre, WatchedTVShow
from rest_framework.test import APIClient
from choosr.models import CustomUser


# test for the questionnaire / advanced questionnaire for tv
# also an integration test as we test the view, the database, and response format
# creates 8 Tv show objects and then applies answers as filters to return them correctly
class TVShowListViewTest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        comedy_genre = Genre.objects.create(id="35")
        # create 8 TV shows
        for i in range(8):
            TVShow.objects.create(
                id=i,
                name=f"Show {i}",
                overview="This is an overview",
                first_air_date="2022-01-01",
                origin_country="US",
                popularity=5.5,
                status="Running",
                poster_path="/xy{i}",
                number_of_seasons=3,
                episode_run_time=30,
                last_air_date="2022-08-01",
            ).genres.add(comedy_genre)

        # create additional tv show for filtering
        TVShow.objects.create(
                id=10,
                name="Show 10",
                overview="This is an overview",
                first_air_date="2022-01-01",
                origin_country="US",
                popularity=5.5,
                status="Running",
                poster_path="/xy10",
                number_of_seasons=1,
                episode_run_time=30,
                last_air_date="2022-08-01",
            ).genres.add(comedy_genre)

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
            'origin': answers['origin'],
            'seasons': None if answers['seasons'] == 'Indifferent' else answers['seasons'],
            'status': answers['status'],

        }

    def test_tvshow_list_view(self):
        answers = {
            'content_type': 'TV',
            'genre': 'Comedy',
            'mainstream': 'No',
            'period': 'Current',
            'length': '30mins',
            'origin': 'North America',
            'seasons': '3-4',
            'status': 'No'
        }
        mapped_answers = self.map_answers(answers)
        backend_url = f"http://localhost:8000/{mapped_answers['content_type']}/"

        response = self.client.get(backend_url, mapped_answers)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 8) # expect 8 shows
        response_data = response.data
        for i in range(8):
            expected_show_name = 'Show ' + str(i)
            actual_show_name = response_data[i]['name']
            self.assertEqual(actual_show_name, expected_show_name) # ensure the expected shows are in the response

    # tests filters are removed correctly
    def test_remove_filters_function(self):
        answers = {
            'content_type': 'TV',
            'genre': 'Comedy',
            'mainstream': 'No',
            'period': 'Current',
            'length': '30mins',
            'origin': 'North America',
            'seasons': '1-2',# causes filters to be removed as only 1 object meets this
            'status': 'No'
        }
        mapped_answers = self.map_answers(answers)
        backend_url = f"http://localhost:8000/{mapped_answers['content_type']}/"
        response = self.client.get(backend_url, mapped_answers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 8) # expect 8 shows after filters are removed

    # tests that specified ids will be excluded from returned querysets
    def test_exclude_ids(self):
        answers = {
            'content_type': 'TV',
            'genre': 'Comedy',
            'mainstream': 'No',
            'period': 'Current',
            'length': '30mins',
            'origin': 'North America',
            'seasons': '3-4',
            'status': 'No'
        }
        exclude_ids = "3"

        mapped_answers = self.map_answers(answers)
        mapped_answers['exclude'] = exclude_ids
        backend_url = f"http://localhost:8000/{mapped_answers['content_type']}/"

        response = self.client.get(backend_url, mapped_answers)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 7)  # expect 7 shows since 1 is excluded
        excluded_show_names = "Show 3"
        response_data = response.data
        for show in response_data:
            self.assertNotIn(show['name'], excluded_show_names)  # assert that excluded shows are not in the response


# set up a tv show that the following tests can add and remove
class BaseWatchedTVShowTest(APITestCase):
    def setUp(self):
        comedy_genre = Genre.objects.create(id="35")
        self.tvshow = TVShow.objects.create(
            id=1,
            name="Show 1",
            overview="This is an overview",
            first_air_date="2022-01-01",
            origin_country="US",
            popularity=5.5,
            status="Running",
            poster_path="/xy1",
            number_of_seasons=3,
            episode_run_time=30,
            last_air_date="2022-08-01",
        )
        self.tvshow.genres.add(comedy_genre)
        # create a user to add / remove the show
        self.user = CustomUser.objects.create_user(username='testuser', email='test@example.com',
                                                   date_of_birth='2000-01-01', password='thisissecure')
        self.client = APIClient()

class AddWatchedTVShowTest(BaseWatchedTVShowTest):
    def setUp(self):
        super().setUp()
        self.url = reverse('add-watched-tvshow')
    def test_add_watched_tvshow_authenticated(self):
        # force authenticates a user
        self.client.force_authenticate(user=self.user)
        # sends the id to be added
        response = self.client.post(self.url, {'tv_id': self.tvshow.id})
        # status 200 means successful add
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # users watched tv shows should have a total of 1 now
        self.assertEqual(WatchedTVShow.objects.filter(user=self.user, tvshow__id=self.tvshow.id).count(), 1)

    def test_add_watched_tvshow_unauthenticated(self):
        # without authentication the request should fail
        response = self.client.post(self.url, {'tv_id': self.tvshow.id})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


# same as addition with different url 
class RemoveWatchedTVShowTest(BaseWatchedTVShowTest):
    def setUp(self):
        super().setUp()
        WatchedTVShow.objects.create(user=self.user, tvshow=self.tvshow)
        self.url = reverse('remove-watched-tvshow')

    def test_remove_watched_tvshow_authenticated(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.url, {'tv_id': self.tvshow.id})
        self.assertEqual(response.status_code,
                         status.HTTP_204_NO_CONTENT)

    def test_remove_watched_tvshow_unauthenticated(self):
        response = self.client.post(self.url, {'tv_id': self.tvshow.id})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class DualRecommendTVTest(APITestCase):

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
        # Create TV shows
        self.tv_show1 = TVShow.objects.create(
            id=1,
            name="Show 1",
            overview="This is an overview",
            first_air_date="2020-03-11",
            origin_country="US",
            popularity=27.0,
            status="Running",
            poster_path="/xy1",
            number_of_seasons=3,
            episode_run_time=30,
            last_air_date="2032-06-01"
        )
        self.tv_show1.genres.add(self.genre1)

        self.tv_show2 = TVShow.objects.create(
            id=2,
            name="Show 2",
            overview="This is an overview",
            first_air_date="2012-01-01",
            origin_country="UK",
            popularity=12.0,
            status="Running",
            poster_path="/xy2",
            number_of_seasons=5,
            episode_run_time=60,
            last_air_date="2017-08-01"
        )
        self.tv_show2.genres.add(self.genre2)
        # Create Watched TV Shows
        WatchedTVShow.objects.create(user=self.user1, tvshow=self.tv_show1)
        WatchedTVShow.objects.create(user=self.user2, tvshow=self.tv_show2)

        genres = [self.genre1, self.genre2]
        # creating 16 tv shows, alternating between odd and even to mix values
        for i in range(3, 19):  # IDs start from 3 since 1 and 2 are already used
            tv_show = TVShow.objects.create(
                id=i,
                name=f"Show {i}",
                overview="This is an overview",
                first_air_date="2022-01-01" if i % 2 == 0 else "2020-01-01",
                origin_country="UK" if i % 2 == 0 else "US",
                popularity=7.0 if i % 2 == 0 else 12.0,
                status="Running" if i % 2 == 0 else "Ended",
                poster_path=f"/xy{i}",
                number_of_seasons=2 if i % 2 == 0 else 5,
                episode_run_time=60 if i % 2 == 0 else 45,
                last_air_date="2022-08-01"
            )
            tv_show.genres.add(genres[i % 2])

    def test_get_recommendations(self):
        client = APIClient()
        client.force_authenticate(user=self.user1)
        url = reverse('dual-recommend-tv', args=[self.user1.email, self.user2.email])
        response = client.get(url)
        self.assertEqual(response.status_code, 200)  # Check the response is successful

        # Ensure the watched shows are not in the recommendations
        watched_shows_ids = [self.tv_show1.id, self.tv_show2.id]
        recommended_shows_ids = [show['id'] for show in response.data]
        for watched_show_id in watched_shows_ids:
            self.assertNotIn(watched_show_id, recommended_shows_ids) # watch list items should not be returned

        self.assertEqual(len(response.data), 8) # only 8 items should be returned at a time

        # Get the recommended shows from the response
        recommended_shows = TVShow.objects.filter(id__in=[show['id'] for show in response.data])

        # Define the set of genres associated with user1 and user2
        user_genres = {self.genre1.id, self.genre2.id}

        # Iterate through the recommended shows and perform assertions
        for show in recommended_shows:
            show_genres = {genre.id for genre in show.genres.all()}
            # Check if at least one of the user genres is present in the recommended shows
            self.assertTrue(user_genres.intersection(show_genres))

        for show in response.data:
            # ensure the attributes are in the correct range
            air_date = datetime.strptime(show['first_air_date'], '%Y-%m-%d').date()
            self.assertGreaterEqual(air_date, date(2012, 1, 1))
            self.assertLessEqual(air_date, date(2020, 12, 31))
            self.assertIn(show['episode_run_time'], [45, 60])
            self.assertIn(show['number_of_seasons'], [2, 5])
            self.assertIn(show['episode_run_time'], [45, 60])










