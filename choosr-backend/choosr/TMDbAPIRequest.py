import requests
from django.db import transaction
from choosr.models import Movie, TVShow, Genre
import datetime
from django.core.exceptions import ValidationError


# Function to process a single TV show item
def process_tv_show(item):
    # takes tv id and makes request for additional details not provided by discover
    details_url = f"https://api.themoviedb.org/3/tv/{item['id']}?api_key=f6071a36fe3772a3c41f7a3558f56c35"

    response = requests.get(details_url)
    if response.status_code == 200:
        details = response.json()
        number_of_seasons = details.get('number_of_seasons', None)
        episode_run_time = min(details.get('episode_run_time', [None])) if details.get('episode_run_time') else None
        last_air_date = details.get('last_air_date', None)
        status = details.get('status', '')

    # Process the release date (formatting issues can occur)
    release_date = item.get('first_air_date')
    if release_date is not None:
        try:
            # Check if the date is in the expected format
            datetime.datetime.strptime(release_date, '%Y-%m-%d')
        except ValueError:
            # If the date is not in the expected format, set the date to a noticeable default
            release_date = '1900-01-01'
    else:
        # If the date is not available, set the date to the default
        release_date = '1900-01-01'

    genre_ids = item['genre_ids']
    genres = []

    for genre_id in genre_ids:
        # Check if the genre with the current ID already exists in the database
        try:
            genre = Genre.objects.get(id=genre_id)
        except Genre.DoesNotExist:
            # If the genre does not exist, create a new Genre object and save it to the database
            genre = Genre.objects.create(id=genre_id)
        genres.append(genre)

    # Create a new TVShow object with the provided data
    tv_show = TVShow(
        id=item['id'],
        name=item['name'],
        overview=item['overview'],
        first_air_date=release_date,
        origin_country=item['origin_country'],
        popularity=item['popularity'],
        poster_path=item['poster_path'],
        number_of_seasons=number_of_seasons,
        episode_run_time=episode_run_time,
        last_air_date=last_air_date,
        status=status,
    )

    # Save the TVShow object to the database
    try:
        tv_show.save()
        tv_show.genres.set(genres)

    # if the tv show cannot be saved, print an error
    except ValidationError as e:
        print(f"Error saving TV show {tv_show.name}: {e}")


# Function to process a single movie item
def process_movie(item):
    details_url = f"https://api.themoviedb.org/3/movie/{item['id']}?api_key=f6071a36fe3772a3c41f7a3558f56c35"
    response = requests.get(details_url)
    if response.status_code == 200:
        details = response.json()
        belongs_to_collection = details.get('belongs_to_collection', None)
        if belongs_to_collection is not None:
            belongs_to_collection = belongs_to_collection.get('name', '')
        else:
            belongs_to_collection = ''

        runtime = details.get('runtime', None)
        budget = details.get('budget', None)
        revenue = details.get('revenue', None)

        release_date = item.get('release_date')
        if release_date is not None:
            try:
                # Check if the date is in the expected format
                datetime.datetime.strptime(release_date, '%Y-%m-%d')
            except ValueError:
                # If the date is not in the expected format, set the date to a default value
                release_date = '1900-01-01'
        else:
            # If the date is not available, set the date to a default value
            release_date = '1900-01-01'

        genre_ids = item['genre_ids']
        genres = []

        for genre_id in genre_ids:
            # Check if the genre with the current ID already exists in the database
            try:
                genre = Genre.objects.get(id=genre_id)
            except Genre.DoesNotExist:
                # If the genre does not exist, create a new Genre object and save it to the database
                genre = Genre.objects.create(id=genre_id)
            genres.append(genre)

        # Create a new movie object with the provided data
        movie = Movie(
            id=item['id'],
            title=item['title'],
            overview=item['overview'],
            release_date=release_date,
            popularity=item['popularity'],
            poster_path=item['poster_path'],
            belongs_to_collection=belongs_to_collection,
            runtime=runtime,
            budget=budget,
            revenue=revenue,
        )
        # Save the movie object to the database
        try:
            movie.save()
            movie.genres.set(genres)
        # if the movie cannot be saved, print an error
        except ValidationError as e:
            print(f"Error saving Movie: {movie.title}: {e}")


# Function to retrieve and process all TV shows - atomic transaction means no data will be saved if any error occurs
@transaction.atomic
def retrieve_all_tv_shows():
    # request format as outlined on TMDBs website
    url = "https://api.themoviedb.org/3/discover/tv"
    headers = {
        "accept": "application/json",
        "Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiJmNjA3MWEzNmZlMzc3MmEzYzQxZjdhMzU1OGY1NmMzNSIsInN1YiI6IjY0YWJlZmQzM2UyZWM4MDBhZjdlNjYxYiIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.FRdlckEGD9yATBdXQ18yvQqT656qBzwqUappgjscI98"
    }
    # some of the parameters offered by TMDB for filtering
    params = {
        "include_adult": "false",
        "include_null_first_air_dates": "false",
        "with_original_language": "en",
        "sort_by": "popularity.desc",
        "page": 1  # Start with page 1, actually not possible to start from >500
    }
    # Get total_pages from the first response
    response = requests.get(url, headers=headers, params=params)

    if response.status_code != 200:
        print("Error retrieving data from TMDb API")
        print(response)
        return

    data = response.json()
    total_pages = data['total_pages']

    for page in range(1, min(total_pages + 1, 501)):  # limited to 500 pages (API max for one request)
        print(f"TV Page: ", page)
        params['page'] = page
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:  # status code 200 is a success response
            data = response.json()
            # Process each TV show item on the current page
            for item in data['results']:
                process_tv_show(item)
        # if there is an error print the information
        else:
            print(f"Error on page {page}")
            print(f"Status code: {response.status_code}")
            print(f"Response body: {response.text}")


# Function to retrieve and process all movies
@transaction.atomic
def retrieve_all_movies():
    url = "https://api.themoviedb.org/3/discover/movie"
    headers = {
        "accept": "application/json",
        "Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiJmNjA3MWEzNmZlMzc3MmEzYzQxZjdhMzU1OGY1NmMzNSIsInN1YiI6IjY0YWJlZmQzM2UyZWM4MDBhZjdlNjYxYiIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.FRdlckEGD9yATBdXQ18yvQqT656qBzwqUappgjscI98"
    }
    params = {
        "include_adult": "false",
        "with_original_language": "en",
        "sort_by": "popularity.desc",
        "page": 1  # Start with page 1, actually not possible to start from >500
    }
    # Get total_pages from the first response
    response = requests.get(url, headers=headers, params=params)
    if response.status_code != 200:
        print("Error retrieving data from TMDb API")
        print(response)
        return

    data = response.json()
    total_pages = data['total_pages']

    for page in range(1, min(total_pages + 1, 501)): # 500 pages is max for tmdb request
        params['page'] = page
        print(f"Movie Page: ", page)
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            data = response.json()
            # Process each movie item on the current page
            for item in data['results']:
                process_movie(item)
        else:
            print(f"Error on page {page}")
            print(f"Status code: {response.status_code}")
            print(f"Response body: {response.text}")








