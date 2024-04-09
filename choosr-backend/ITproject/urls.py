"""ITproject URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

from choosr.views import UserRegister, UserLogin, UserLogout, MovieListView, TVShowListView, AddWatchedMovie, \
    AddWatchedTVShow, WatchedMovies, WatchedTVShows, RemoveWatchedTVShow, RemoveWatchedMovie, DualRecommendMovie, \
    DualRecommendTV, RemoveAllWatched, TopPicks, TimeTakenUnregisteredView, TimeTakenRegisteredView
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls')), # https://www.django-rest-framework.org/tutorial/4-authentication-and-permissions/
    path('register/', UserRegister.as_view(), name='register'),
    path('login/', UserLogin.as_view(), name='login'),
    path('logout/', UserLogout.as_view(), name='logout'),
    path('movie/', MovieListView.as_view(), name='movie'),
    path('tv/', TVShowListView.as_view(), name='tv'),
    path('add-watched-movie/', AddWatchedMovie.as_view(), name='add-watched-movie'),
    path('add-watched-tv/', AddWatchedTVShow.as_view(), name='add-watched-tvshow'),
    path('remove-watched-movie/', RemoveWatchedMovie.as_view(), name='remove-watched-movie'),
    path('remove-watched-tv/', RemoveWatchedTVShow.as_view(), name='remove-watched-tvshow'),
    path('remove-all-watched/', RemoveAllWatched.as_view(), name='remove-all-watched'),
    path('watched-movies/', WatchedMovies.as_view(), name='watched-movies'),
    path('watched-tvshows/', WatchedTVShows.as_view(), name='watched-tvshows'),
    path('watched-movies/<str:email>/', WatchedMovies.as_view(), name='friend-watched-movies'),
    path('watched-tvshows/<str:email>/', WatchedTVShows.as_view(), name='friend-watched-tvshows'),
    path('dual-recommend-movie/<str:email1>/<str:email2>/', DualRecommendMovie.as_view(), name='dual-recommend-movie'),
    path('dual-recommend-tv/<str:email1>/<str:email2>/', DualRecommendTV.as_view(), name='dual-recommend-tv'),
    path('top-picks/', TopPicks.as_view(), name='top-picks'),
    path('save-time-taken-unregistered/', TimeTakenUnregisteredView.as_view(), name='time-taken-unregistered'),
    path('save-time-taken-registered/', TimeTakenRegisteredView.as_view(), name='time-taken-registered'),
    path('', TemplateView.as_view(template_name='build/index.html')),
]



