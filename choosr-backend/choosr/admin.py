from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth import get_user_model
from .models import WatchedMovie, WatchedTVShow

User = get_user_model()

class CustomUserAdmin(UserAdmin):
    pass

admin.site.register(User, CustomUserAdmin)
admin.site.register(WatchedMovie)
admin.site.register(WatchedTVShow)






