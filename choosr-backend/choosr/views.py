from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework import status
from rest_framework.generics import ListAPIView
from choosr.forms import UserForm
from choosr.serializers import UserSerializer, UserLoginSerializer, MovieSerializer, TVShowSerializer
from choosr.models import Movie, TVShow, WatchedMovie, WatchedTVShow, TimeTakenRegistered, TimeTakenUnregistered
from django.contrib.auth import login, logout
from datetime import datetime
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from rest_framework.pagination import BasePagination
from django.contrib.auth import get_user_model
from collections import Counter
from django.db.models import Avg

# this file could be abstracted in places but was not done yet as time constraints meant changing functions was risky
# this can be done in the future by separating certain functions into different files and abstracting those with similar
# logic.

# these mappings take frontend descriptions and match it to database value
GENRE_NAME_TO_ID = {"Action": "28", "Adventure": "12", "Action & Adventure": "10759", "Animation": "16",
                    "Comedy": "35", "Crime": "80", "Documentary": "99", "Drama": "18", "Family": "10751",
                    "Kids": "10762", "Fantasy": "14", "History": "36", "Horror": "27", "Music": "10402",
                    "Mystery": "9648", "News": "10763", "Romance": "10749", "Reality": "10764", "Soap": "10766",
                    "Sci-Fi & Fantasy": "10765", "Science Fiction": "878", "Talk": "10767", "Tv Movie": "10770",
                    "Thriller": "53", "War": "10752", "War & Politics": "10768", "Western": "37", }

ORIGIN_MAPPING = {'North America': ['US', 'CA'], 'United Kingdom': ['GB'], 'Oceania': ['AU', 'NZ'] }


# register view that sets up a user account based off correct information
class UserRegister(APIView):
    def post(self, request):
        user_form = UserForm(request.data)
        if user_form.is_valid():
            user = user_form.save()  # UserCreationForm already handles password confirmation and hashing.
            serializer = UserSerializer(user)
            response_data = serializer.data
            response_data['registered'] = True
            return Response(response_data, status=status.HTTP_201_CREATED)
        else:
            return Response(user_form.errors, status=status.HTTP_400_BAD_REQUEST)


# login view that checks the user is valid and provides a token if so
class UserLogin(APIView):
    def post(self, request, *args, **kwargs):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data
            login(request, user)
            token, created = Token.objects.get_or_create(user=user)
            user_data = UserSerializer(user).data
            return Response({'token': token.key, 'message': 'Login Successful', 'user': user_data})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# logout view that deletes token associated with user session
class UserLogout(APIView):
    def post(self, request, *args, **kwargs):
        request.user.auth_token.delete()
        logout(request)
        return Response({'message': 'Logout successful'}, status=status.HTTP_200_OK)


class CustomPagination(BasePagination):
    def paginate_queryset(self, queryset, request, view=None):
        return queryset[:8] # limited to 8 so users are not overwhelmed with content

    # handles data serialisation
    def get_paginated_response(self, data):
        return Response(data)


class TVShowListView(ListAPIView):
    queryset = TVShow.objects.all()
    pagination_class = CustomPagination
    serializer_class = TVShowSerializer
    filter_set_fields = ['genres__id', 'first_air_date', 'popularity', 'episode_run_time',
                         'origin_country', 'number_of_seasons', 'status']


    def get_queryset(self):
        queryset = super().get_queryset()
        params = self.request.query_params
        queryset = self.apply_all_filters(queryset, params)

        # Check if the result is less than 8 and call remove_filters if necessary
        if queryset.count() < 8:
            queryset = self.remove_filters()

        # excludes tv shows user has encountered already in content list and watch lists
        exclude = self.request.query_params.get('exclude', None)
        if exclude is not None:
            exclude_ids = [int(id) for id in exclude.split(',')]
            queryset = queryset.exclude(id__in=exclude_ids)

        return queryset

    # series of methods below represent the filters for user preferences

    def filter_genre(self, queryset, params):
        genre = params.get('genre', None)
        if genre is not None:
            genre_id = GENRE_NAME_TO_ID.get(genre)
            if genre_id is not None:
                queryset = queryset.filter(genres__id=genre_id)

        return queryset

    def filter_mainstream(self, queryset, params):
        mainstream = params.get('mainstream', None)
        if mainstream == '>10':
            queryset = queryset.filter(popularity__gt=10)
        elif mainstream == '<=10':
            queryset = queryset.filter(popularity__lte=10)
        return queryset

    def filter_period(self, queryset, params):
        period = params.get('period', None)
        if period is not None:
            if period == "Current":
                start_date = datetime(2020, 1, 1)
                end_date = datetime.now()
                queryset = queryset.filter(first_air_date__gte=start_date, first_air_date__lte=end_date)
            elif period == "<1970":
                start_date = datetime(1940, 1, 1) # based on items in DB
                end_date = datetime(1979, 12, 31)
                # this was the default date set for items without a first_air_date so they are likely in the future too
                # / cannot be watched
                exclude_date = datetime(1900, 1, 1)
                queryset = queryset.filter(first_air_date__range=(start_date, end_date)).exclude(
                    first_air_date=exclude_date)
            elif period.isdigit():
                period_start = datetime(int(period), 1, 1)
                period_end = datetime(int(period) + 10, 1, 1)
                queryset = queryset.filter(first_air_date__range=(period_start, period_end))
        return queryset

    def filter_episode_run_time(self, queryset, params):
        episode_run_time = params.get('length', None)
        if episode_run_time == '15mins':
            queryset = queryset.filter(episode_run_time__range=(0, 20))
        elif episode_run_time == '30mins':
            queryset = queryset.filter(episode_run_time__range=(20, 40))
        elif episode_run_time == '45mins':
            queryset = queryset.filter(episode_run_time__range=(40, 55))
        elif episode_run_time == '60mins':
            queryset = queryset.filter(episode_run_time__range=(55, 65))
        elif episode_run_time == '>60mins':
            queryset = queryset.filter(episode_run_time__gt=65)
        return queryset

    def filter_origin_country(self, queryset, params):
        origin_country = params.get('origin', None)
        if origin_country and origin_country != 'Anywhere':
            origin_country_codes = ORIGIN_MAPPING.get(origin_country, [])
            origin_country_filter = Q()
            for code in origin_country_codes:
                origin_country_filter |= Q(origin_country__icontains=code)
            queryset = queryset.filter(origin_country_filter)
        return queryset

    def filter_number_of_seasons(self, queryset, params):
        number_of_seasons = params.get('seasons', None)
        if number_of_seasons == '1-2':
            queryset = queryset.filter(number_of_seasons__range=(1, 2))
        elif number_of_seasons == '3-4':
            queryset = queryset.filter(number_of_seasons__range=(3, 4))
        elif number_of_seasons == '5-6':
            queryset = queryset.filter(number_of_seasons__range=(5, 6))
        elif number_of_seasons == '7+':
            queryset = queryset.filter(number_of_seasons__gte=7)
        return queryset

    def filter_status(self, queryset, params):
        status = params.get('status', None)
        if status is not None and status != 'Indifferent':
            if status == 'Yes':
                queryset = queryset.filter(status__iexact='Returning Series')
            elif status == 'No':
                queryset = queryset.filter(Q(status__contains='Ended') | Q(status__contains='Canceled'))
        return queryset

    def apply_all_filters(self, queryset, params, exclude_filters=[]):
        # Apply all methods that start with "filter" except the built-in filter_queryset
        # This could be done in a better way, perhaps improve in future
        for method_name in dir(self):
            if method_name.startswith('filter_') and method_name != 'filter_queryset' and \
                    method_name not in exclude_filters:
                filter_method = getattr(self, method_name)
                if callable(filter_method):
                    queryset = filter_method(queryset, params)
        return queryset

    def remove_filters(self):
        filter_priority = [
            'filter_origin_country', 'filter_period', 'filter_status',
            'filter_number_of_seasons', 'filter_mainstream', 'filter_episode_run_time', 'filter_genre',
        ]
        removed_filters = []  # Keep track of the filters that get removed

        # Iterate through filters in priority order
        for filter_name in filter_priority:
            queryset = TVShow.objects.all() # Start with the original queryset with no filters applied
            removed_filters.append(filter_name)
            # Reapply all filters except the ones that have been removed
            queryset = self.apply_all_filters(queryset, self.request.query_params, removed_filters)
            # Once count is enough, break the loop
            if queryset.count() >= 8:
                return queryset

    # this function handles serialisation and pagination of the list of objects from the database
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serialized_data = self.get_serializer(page, many=True).data
            return self.get_paginated_response(serialized_data)
        serialized_data = self.get_serializer(queryset, many=True).data
        return Response(serialized_data)


# same set up as TV View, could mean abstraction is needed later
class MovieListView(ListAPIView):
    queryset = Movie.objects.all()
    pagination_class = CustomPagination
    serializer_class = MovieSerializer
    filter_set_fields = ['genres__id', 'release_date', 'popularity', 'runtime',
                         'belongs_to_collection', 'budget', 'revenue']

    def get_queryset(self):
        queryset = super().get_queryset()
        params = self.request.query_params
        queryset = self.apply_all_filters(queryset, params)

        # Check if the result is less than 8 and call remove_filters if necessary
        if queryset.count() < 8:
            queryset = self.remove_filters()

        # excludes what user has encountered already
        exclude = self.request.query_params.get('exclude', None)
        if exclude is not None:
            exclude_ids = [int(id) for id in exclude.split(',')]
            queryset = queryset.exclude(id__in=exclude_ids)

        return queryset

    def filter_genre(self, queryset, params):
        genre = params.get('genre', None)
        if genre is not None:
            genre_id = GENRE_NAME_TO_ID.get(genre)
            if genre_id is not None:
                queryset = queryset.filter(genres__id=genre_id)
        return queryset

    def filter_mainstream(self, queryset, params):
        mainstream = params.get('mainstream', None)
        if mainstream is not None:
            queryset = queryset.filter(popularity__gt=25) if mainstream == '>25' else queryset.filter(
                popularity__lte=25)
        return queryset


    def filter_period(self, queryset, params):
        period = params.get('period', None)
        if period is not None:
            if period == "Current":
                start_date = datetime(2020, 1, 1)  # anything from 2020 onwards as current
                end_date = datetime.now()
                queryset = queryset.filter(release_date__gte=start_date, release_date__lte=end_date)
            elif period == "<1970":
                start_date = datetime(1920, 1, 1)  # based on items in db
                end_date = datetime(1979, 12, 31)
                exclude_date = datetime(1900, 1, 1)  # exclude "1900-01-01"
                queryset = queryset.filter(release_date__range=(start_date, end_date)).exclude(
                    release_date=exclude_date)
            elif period.isdigit():
                period_start = datetime(int(period), 1, 1)
                period_end = datetime(int(period) + 10, 1, 1)
                queryset = queryset.filter(release_date__range=(period_start, period_end))
        return queryset

    def filter_runtime(self, queryset, params):
        length = params.get('length', None)
        if length is not None:
            if length == '60mins':
                queryset = queryset.filter(runtime__lte=70)
            elif length == '90mins':
                queryset = queryset.filter(runtime__gte=70, runtime__lte=110)
            elif length == '120mins':
                queryset = queryset.filter(runtime__gte=110, runtime__lte=130)
            elif length == '>120mins':
                queryset = queryset.filter(runtime__gte=130)
        return queryset

    def filter_collection(self, queryset, params):
        collection = params.get('collection', None)
        # handle null and empty values in database
        if collection == 'Yes':
            queryset = queryset.exclude(Q(belongs_to_collection__isnull=True) | Q(belongs_to_collection=''))
        elif collection == 'No':
            queryset = queryset.filter(Q(belongs_to_collection__isnull=True) | Q(belongs_to_collection=''))
        return queryset

    # budget and revenue values chosen based on average number of films matching this in database
    def filter_budget(self, queryset, params):
        budget = params.get('budget', None)
        if budget == 'Yes':
            queryset = queryset.filter(budget__gt=10000000)
        elif budget == 'No':
            queryset = queryset.filter(budget__lte=10000000)
        return queryset

    def filter_revenue(self, queryset, params):
        revenue = params.get('revenue', None)
        if revenue == 'Yes':
            queryset = queryset.filter(revenue__gt=10000000)
        elif revenue == 'No':
            queryset = queryset.filter(revenue__lte=10000000)
        return queryset

    # method called by the request to filter based on the parameters provided by the user
    def apply_all_filters(self, queryset, params, exclude_filters=[]):
        for method_name in dir(self):
            if method_name.startswith('filter_') and method_name != 'filter_queryset' and \
                    method_name not in exclude_filters:  # don't want to repeat filters
                filter_method = getattr(self, method_name)
                if callable(filter_method):
                    queryset = filter_method(queryset, params)
        return queryset

    def remove_filters(self):
        filter_priority = [
            'filter_revenue', 'filter_budget', 'filter_collection', 'filter_period', 'filter_mainstream',
            'filter_runtime', 'filter_genre',
        ]
        # Keep track of the filters that have been removed
        removed_filters = []

        # Iterate through filters in priority order
        for filter_name in filter_priority:
            queryset = Movie.objects.all() # Start with the original queryset with no filters applied
            removed_filters.append(filter_name)

            # Reapply all filters except the ones that have been removed
            queryset = self.apply_all_filters(queryset, self.request.query_params, removed_filters)

            # Once count is enough, return the results
            if queryset.count() >= 8:
                return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serialized_data = self.get_serializer(page, many=True).data
            return self.get_paginated_response(serialized_data)
        serialized_data = self.get_serializer(queryset, many=True).data
        return Response(serialized_data)


class AddWatchedMovie(APIView):
    permission_classes = [IsAuthenticated] # only authenticated users can access this method

    def post(self, request):
        movie_id = request.data.get('movie_id')
        movie = Movie.objects.get(id=movie_id)
        user = request.user
        WatchedMovie.objects.create(user=user, movie=movie)
        return Response({"message": "Movie added to watched list"})


class AddWatchedTVShow(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        tvshow_id = request.data.get('tv_id')  # 'tv'_id important for matching client-side
        tvshow = TVShow.objects.get(id=tvshow_id)
        user = request.user
        WatchedTVShow.objects.create(user=user, tvshow=tvshow)
        return Response({"message": "TV show added to watched list"})


class RemoveWatchedMovie(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = request.user
        movie = get_object_or_404(Movie, id=request.data.get('movie_id')) # in testing changed this from id to movie_id
        watched_movie = get_object_or_404(WatchedMovie, user=user, movie=movie)
        watched_movie.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class RemoveWatchedTVShow(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = request.user
        tvshow_id = request.data.get('tv_id')
        tvshow = get_object_or_404(TVShow, id=tvshow_id)
        watched_tvshow = get_object_or_404(WatchedTVShow, user=user, tvshow=tvshow)
        watched_tvshow.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class RemoveAllWatched(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = request.user
        WatchedMovie.objects.filter(user=user).delete()
        WatchedTVShow.objects.filter(user=user).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# these classes handle retrieving a users watched movies and tv shows
# also allows users to see another users watched without any permission handling
# as the data being dealt with is not sensitive the permission handling is not urgent but should be fixed in future
class WatchedMovies(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, email=None, *args, **kwargs):
        if email:
            user = get_object_or_404(get_user_model(), email=email)
        else:
            user = request.user

        watched_movies = WatchedMovie.objects.filter(user=user)
        serializer = MovieSerializer([watched_movie.movie for watched_movie in watched_movies], many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class WatchedTVShows(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, email=None, *args, **kwargs):
        if email:
            user = get_object_or_404(get_user_model(), email=email)
        else:
            user = request.user

        watched_tvshows = WatchedTVShow.objects.filter(user=user)
        serializer = TVShowSerializer([watched_tvshow.tvshow for watched_tvshow in watched_tvshows], many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


# more detailed comments of dual recommend under TV version
class DualRecommendMovie(APIView):
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination
    serializer_class = MovieSerializer

    def get(self, request, email1, email2, format=None):

        # Retrieve Watched Items
        watched_movies1 = self.get_watched_movies(email1)
        watched_movies2 = self.get_watched_movies(email2)
        watched_movie_ids = [movie.id for movie in watched_movies1 + watched_movies2]

        # exclude content the user has already been shown for refreshing
        exclude = request.query_params.get('exclude', None)
        if exclude is not None:
            exclude_ids = [int(id) for id in exclude.split(',')]
            watched_movie_ids.extend(exclude_ids)

        # Extract Attributes
        attributes1 = self.extract_attributes(watched_movies1)
        attributes2 = self.extract_attributes(watched_movies2)

        # Compare Attributes
        common_attributes = self.compare_attributes(attributes1, attributes2)

        # Apply Filters
        recommendations = self.apply_filters(common_attributes, watched_movie_ids)

        # if less than 8 are returned, refine the filters
        if recommendations.count() < 8:
            recommendations = self.refine_common_attributes(common_attributes, watched_movie_ids)

        # Paginate the recommendations using the custom pagination class
        page = self.pagination_class().paginate_queryset(recommendations, request, view=self)

        if page is not None:
            serialized_data = MovieSerializer(page, many=True).data
            return self.pagination_class().get_paginated_response(serialized_data)

        # If not using pagination or for the last page
        serialized_data = MovieSerializer(recommendations, many=True).data
        return Response(serialized_data)


    def get_watched_movies(self, email):
        user = get_object_or_404(get_user_model(), email=email)
        watched_movies = WatchedMovie.objects.filter(user=user).select_related('movie')
        return [watched_movie.movie for watched_movie in watched_movies]

    def apply_all_filters(self, queryset, params):
        for method_name in dir(self):
            if method_name.startswith('filter_'):
                filter_method = getattr(self, method_name)
                if callable(filter_method):
                    queryset = filter_method(queryset, params)
        return queryset

    def apply_filters(self, common_attributes, watched_movie_ids):
        queryset = Movie.objects.all()
        queryset = queryset.exclude(id__in=watched_movie_ids) # stops users being given items they have already watched
        queryset = self.apply_all_filters(queryset, common_attributes)
        queryset = queryset.distinct() # added this line after switching from sqlite to postgres as duplicates were returned
        return queryset

    # loops through attributes and returns them
    def extract_attributes(self, watched_movies):
        attributes = {
            'genres': set(),
            'release_date': [],
            'popularity': [],
            'belongs_to_collection': set(),
            'runtime': [],
            'budget': [],
            'revenue': []
        }
        for movie in watched_movies:
            attributes['genres'].update(movie.genres.all())
            attributes['release_date'].append(movie.release_date)
            attributes['popularity'].append(movie.popularity)
            if movie.belongs_to_collection:
                attributes['belongs_to_collection'].add(movie.belongs_to_collection)
            attributes['runtime'].append(movie.runtime)
            attributes['budget'].append(movie.budget)
            attributes['revenue'].append(movie.revenue)

        return attributes

    def sort_values(self, attr1, attr2):
        # remove none values
        filtered_attr1 = [x for x in attr1 if x is not None]
        filtered_attr2 = [x for x in attr2 if x is not None]

        min_value = None
        max_value = None

        if filtered_attr1:
            min_value = min(filtered_attr1)
            max_value = max(filtered_attr1)

        if filtered_attr2:
            min_value = min(min_value, min(filtered_attr2)) if min_value else min(filtered_attr2)
            max_value = max(max_value, max(filtered_attr2)) if max_value else max(filtered_attr2)

        return min_value, max_value

    def compare_attributes(self, attributes1, attributes2):
        common_attributes = {
            'genres': attributes1['genres'] & attributes2['genres'],
            'release_date_range': self.sort_values(attributes1['release_date'], attributes2['release_date']),
            'popularity_range': self.sort_values(attributes1['popularity'], attributes2['popularity']),
            'collections': attributes1['belongs_to_collection'] & attributes2['belongs_to_collection'],
            'runtime_range': self.sort_values(attributes1['runtime'], attributes2['runtime']),
            'budget_range': self.sort_values(attributes1['budget'], attributes2['budget']),
            'revenue_range': self.sort_values(attributes1['revenue'], attributes2['revenue'])
        }
        return common_attributes

    def refine_common_attributes(self, common_attributes, watched_movie_ids):
        # Priority list, can be used in evaluations to determine exact order
        refinement_priority = [
            'revenue_range', 'budget_range', 'collections',
            'release_date_range', 'popularity_range',  'runtime_range', 'genres'
        ]

        # How much to expand the range for numerical attributes
        expansion_factor = .1
        max_iterations = 10  # Maximum number of iterations for refinement

        for iteration in range(max_iterations):
            refined = False
            # Iterate through attributes in priority order
            for attribute in refinement_priority:
                if attribute in common_attributes:
                    if attribute.endswith('_range'):
                        start, end = common_attributes[attribute]
                        delta = (end - start) * expansion_factor
                        new_range = (start - delta, end + delta)
                        common_attributes[attribute] = new_range

                    elif isinstance(common_attributes[attribute], set):
                        common_attributes[attribute].clear()

            # Apply the refined filters and check if there are enough results
            recommendations = self.apply_filters(common_attributes, watched_movie_ids)

            if recommendations.count() >= 8:
                return recommendations

            refined = True

        # Increment the expansion factor for the next iteration
            if not refined:
                expansion_factor += 0.1

        # whilst unlikely for max iterations to be hit, this may need to be handled better than returning all
        # or, the max iterations could be removed and expansion factor is just increased until results are found
        return Movie.objects.all()


    # functions for applying the different filters
    def filter_genres(self, queryset, params):
        genres = params['genres']
        if genres:
            genre_filter = Q()
            for genre in genres:
                genre_filter |= Q(genres__id=genre.id)
            queryset = queryset.filter(genre_filter)
        return queryset

    # don't have to handle future dates here because all watched list content is added from ListViews above
    def filter_release_date(self, queryset, params):
        release_date_range = params['release_date_range']
        queryset = queryset.filter(release_date__range=release_date_range)
        return queryset

    def filter_popularity(self, queryset, params):
        popularity_range = params['popularity_range']
        if popularity_range:
            min_popularity, max_popularity = popularity_range
            queryset = queryset.filter(popularity__gte=min_popularity, popularity__lte=max_popularity)
        return queryset

    def filter_collections(self, queryset, params):
        collections = params['collections']
        if collections == 'Yes':
            queryset = queryset.exclude(Q(belongs_to_collection__isnull=True) | Q(belongs_to_collection=''))
        elif collections == 'No':
            queryset = queryset.filter(Q(belongs_to_collection__isnull=True) | Q(belongs_to_collection=''))
        return queryset

    def filter_runtime(self, queryset, params):
        runtime_range = params['runtime_range']
        if runtime_range:
            min_runtime, max_runtime = runtime_range
            queryset = queryset.filter(runtime__gte=min_runtime, runtime__lte=max_runtime)
        return queryset

    def filter_budget(self, queryset, params):
        budget_range = params['budget_range']
        if budget_range:
            min_budget, max_budget = budget_range
            queryset = queryset.filter(budget__gte=min_budget, budget__lte=max_budget)
        return queryset

    def filter_revenue(self, queryset, params):
        revenue_range = params['revenue_range']
        if revenue_range:
            min_revenue, max_revenue = revenue_range
            queryset = queryset.filter(revenue__gte=min_revenue, revenue__lte=max_revenue)
        return queryset


class DualRecommendTV(APIView):
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination
    serializer_class = TVShowSerializer

    def get(self, request, email1, email2, format=None):

        # Retrieve Watched Items
        watched_tv1 = self.get_watched_tvshows(email1)
        watched_tv2 = self.get_watched_tvshows(email2)
        watched_tv_ids = [tvshow.id for tvshow in watched_tv1 + watched_tv2]

        # exclude content the user has already been shown for refreshing
        exclude = request.query_params.get('exclude', None)
        if exclude is not None:
            exclude_ids = [int(id) for id in exclude.split(',')]
            watched_tv_ids.extend(exclude_ids)

        # Extract Attributes
        attributes1 = self.extract_attributes(watched_tv1)
        attributes2 = self.extract_attributes(watched_tv2)

        # Compare Attributes
        common_attributes = self.compare_attributes(attributes1, attributes2)

        # Apply Filters
        recommendations = self.apply_filters(common_attributes, watched_tv_ids)

        # if less than 8 are returned, refine the filters
        if recommendations.count() < 8:
            recommendations = self.refine_common_attributes(common_attributes, watched_tv_ids)

        # Paginate the recommendations using the custom pagination class
        page = self.pagination_class().paginate_queryset(recommendations, request, view=self)

        if page is not None:
            serialized_data = TVShowSerializer(page, many=True).data
            return self.pagination_class().get_paginated_response(serialized_data)

        # If not using pagination or for the last page
        serialized_data = TVShowSerializer(recommendations, many=True).data
        return Response(serialized_data)


    def get_watched_tvshows(self, email):
        user = get_object_or_404(get_user_model(), email=email)
        watched_tvshows = WatchedTVShow.objects.filter(user=user).select_related('tvshow')
        return [watched_tvshow.tvshow for watched_tvshow in watched_tvshows]

    def apply_all_filters(self, queryset, params):
        for method_name in dir(self):
            if method_name.startswith('filter_'):
                filter_name = method_name[7:]  # Extracting the filter name from method name
                filter_method = getattr(self, method_name)
                # by passing the specific filter name, i can see where an issue went wrong easier
                if callable(filter_method) and filter_name in params:
                    queryset = filter_method(queryset, params[filter_name])
        return queryset

    def apply_filters(self, common_attributes, watched_tv_ids):
        queryset = TVShow.objects.all()
        queryset = queryset.exclude(id__in=watched_tv_ids) # stops users being given items they have already watched
        queryset = self.apply_all_filters(queryset, common_attributes) # pass the attributes to applying filters
        queryset = queryset.distinct()
        return queryset

    # takes attributes from users watched lists and sends them back as a dictionary for filtering
    def extract_attributes(self, watched_tvshows):
        attributes = {
            'genres': set(),
            'first_air_date': [],
            'popularity': [],
            'origin_country': set(),
            'episode_run_time': [],
            'status': [],
            'number_of_seasons': []
        }
        for tvshow in watched_tvshows:
            attributes['genres'].update(tvshow.genres.all())
            attributes['first_air_date'].append(tvshow.first_air_date)
            attributes['popularity'].append(tvshow.popularity)
            if tvshow.origin_country:
                attributes['origin_country'].add(tvshow.origin_country)
            attributes['episode_run_time'].append(tvshow.episode_run_time)
            attributes['status'].append(tvshow.status)
            attributes['number_of_seasons'].append(tvshow.number_of_seasons)

        return attributes

    # this function was added after switching from sqlite to postgres as None type errors were occurring
    def sort_values(self, attr1, attr2):
        filtered_attr1 = [x for x in attr1 if x is not None]
        filtered_attr2 = [x for x in attr2 if x is not None]
        min_value = None
        max_value = None

        if filtered_attr1:
            min_value = min(filtered_attr1)
            max_value = max(filtered_attr1)

        if filtered_attr2:
            min_value = min(min_value, min(filtered_attr2)) if min_value else min(filtered_attr2)
            max_value = max(max_value, max(filtered_attr2)) if max_value else max(filtered_attr2)

        return min_value, max_value


    # allows the attributes to be placed on a range by which we can search in
    def compare_attributes(self, attributes1, attributes2):
        # take the origin countries from the attributes
        common_origin_regions = attributes1['origin_country'] & attributes2['origin_country']
        common_origin_countries = set()
        # iterates through the regions to find commons and adds these to the set
        for region in common_origin_regions:
            common_origin_countries.update(ORIGIN_MAPPING.get(region, []))

        common_status = set(attributes1['status']) & set(attributes2['status'])
        if not common_status:
            common_status = None  # if there is no common status just remove the constraint

        common_attributes = {
            'genres': attributes1['genres'] & attributes2['genres'],
            'first_air_date_range': self.sort_values(attributes1['first_air_date'], attributes2['first_air_date']),
            'popularity_range': self.sort_values(attributes1['popularity'], attributes2['popularity']),
            'origin_country': common_origin_countries,
            'number_of_seasons_range': self.sort_values(attributes1['number_of_seasons'],
                                                                 attributes2['number_of_seasons']),
            'episode_run_time_range': self.sort_values(attributes1['episode_run_time'],
                                                                attributes2['episode_run_time']),
            'status': common_status,
        }

        return common_attributes

    def refine_common_attributes(self, common_attributes, watched_tv_ids):
        # Priority list, can be used in evaluations to determine exact order
        # had played with weightings on these as well but its addition seemed to offer limited advantage
        refinement_priority = [
            'origin_country', 'first_air_date_range', 'status',  'number_of_seasons_range', 'popularity_range',
            'episode_run_time_range', 'genres'
        ]

        # checks for common countries and it can include all from origin mapping
        # this may be an issue as origin mapping does not cover every country in db
        if 'origin_country' in common_attributes and not common_attributes['origin_country']:
            refined_countries = set()
            for countries in ORIGIN_MAPPING.values():
                refined_countries.update(countries)
            common_attributes['origin_country'] = refined_countries

        # value to expand the range for numerical attributes, .1 currently seems sufficient
        expansion_factor = .1
        max_iterations = 10  # don't want it to go forever

        # iteration used to handle cases where no attributes are common
        # this is usually when both users only have 1 item each and they are quite different
        for iteration in range(max_iterations):
            refined = False  # Track whether any refinements were made in this iteration

            # Iterate through attributes in priority order
            for attribute in refinement_priority:
                if attribute in common_attributes:
                    if attribute.endswith('_range'):
                        start, end = common_attributes[attribute]
                        delta = (end - start) * expansion_factor
                        new_range = (start - delta, end + delta)
                        common_attributes[attribute] = new_range

                    elif isinstance(common_attributes[attribute], set):
                        common_attributes[attribute].clear()

                    recommendations = self.apply_filters(common_attributes, watched_tv_ids)

                    if recommendations.count() >= 8:
                        return recommendations

                    refined = True

            if not refined:
                expansion_factor += 0.1

        # if after 10 iterations nothing can be found return all so user at least sees something
        return TVShow.objects.all()

    # functions for applying the different filters
    def filter_genres(self, queryset, genres):
        if genres: # Only filter by genres if there is a constraint
            genre_filter = Q()
            for genre in genres:
                genre_filter |= Q(genres__id=genre.id)
            queryset = queryset.filter(genre_filter)
        return queryset

    def filter_first_air_date_range(self, queryset, first_air_date_range):
        queryset = queryset.filter(first_air_date__range=first_air_date_range)
        return queryset

    def filter_popularity_range(self, queryset, popularity_range):
        if popularity_range:
            min_popularity, max_popularity = popularity_range
            queryset = queryset.filter(popularity__gte=min_popularity, popularity__lte=max_popularity)
        return queryset

    def filter_origin_country(self, queryset, origin_country):
        if origin_country:
            queryset = queryset.filter(origin_country__in=origin_country)
        return queryset

    def filter_number_of_seasons_range(self, queryset, number_of_seasons_range):
        if number_of_seasons_range:
            min_seasons, max_seasons = number_of_seasons_range
            queryset = queryset.filter(number_of_seasons__gte=min_seasons, number_of_seasons__lte=max_seasons)
        return queryset

    def filter_episode_run_time_range(self, queryset, episode_run_time_range):
        if episode_run_time_range:
            min_runtime, max_runtime = episode_run_time_range
            queryset = queryset.filter(episode_run_time__gte=min_runtime, episode_run_time__lte=max_runtime)
        return queryset

    def filter_status(self, queryset, status):
        if status:  # Only filter by status if there is a constraint
            queryset = queryset.filter(status__in=status)
        return queryset


# method loops through user watch lists and finds the most watched items
# this could be done more efficiently in future as if lots of users are in the system the time complexity will increase
class TopPicks(APIView):
# no authentication needed as it's for landing page
# may not use all item info but better to have it in the response if i want it displayed in future
    def get_top_picked_movies(self):
        all_watched_movies = [watched.movie for watched in WatchedMovie.objects.all()]
        most_common_movies = Counter(all_watched_movies).most_common(6)  # top 6 most common movies
        top_picks = [
            {
                'id': movie.id,
                'title': movie.title,
                'overview': movie.overview,
                'poster_path': movie.poster_path,
                'release_date': movie.release_date,
                'runtime': movie.runtime
            } for movie, count in most_common_movies
        ]
        return top_picks

    def get_top_picked_tv_shows(self):
        all_watched_tv_shows = [watched.tvshow for watched in WatchedTVShow.objects.all()]
        most_common_tv_shows = Counter(all_watched_tv_shows).most_common(6)  # top 6 most common TV shows
        top_picks = [
            {
                'id': tvshow.id,
                'name': tvshow.name,
                'overview': tvshow.overview,
                'poster_path': tvshow.poster_path,
                'first_air_date': tvshow.first_air_date,
                'episode_run_time': tvshow.episode_run_time
            } for tvshow, count in most_common_tv_shows
        ]
        return top_picks

    # not currently handling if all user watch lists are empty - will just show nothing
    def get(self, request):
        movies = self.get_top_picked_movies()
        tv_shows = self.get_top_picked_tv_shows()
        response_data = {
            'movies': movies,
            'tv_shows': tv_shows
        }
        return Response(response_data)

# some test views to see how long it takes users to get recommendations
# should be removed after testing as will take up too much database storage
class TimeTakenUnregisteredView(APIView):

    def post(self, request):
        time_taken = request.data.get('timeTaken')  # Extract the time taken from the POST data

        record = TimeTakenUnregistered(time_taken=time_taken)
        record.save()

        return Response({'status': 'success'}) # Method Not Allowed if not a POST request


class TimeTakenRegisteredView(APIView):
    def post(self, request):
        time_taken = request.data.get('timeTaken')  # Extract the time taken from the POST data

        record = TimeTakenRegistered(time_taken=time_taken)
        record.save()

        return Response({'status': 'success'}) # Method Not Allowed if not a POST request

# gets the average time and displays it for both registered and unregistered users and the combined average
def AverageTimeTakenForRecommendation():
    avg_unregistered = TimeTakenUnregistered.objects.all().aggregate(Avg('time_taken'))['time_taken__avg']
    avg_registered = TimeTakenRegistered.objects.all().aggregate(Avg('time_taken'))['time_taken__avg']

    print(f"Average time taken for unregistered users: {avg_unregistered} seconds")
    print(f"Average time taken for registered users: {avg_registered} seconds")

    overall_avg = (avg_unregistered + avg_registered) / 2
    print(f"Overall average time taken: {overall_avg} seconds")
