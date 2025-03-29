from django.contrib import admin

from users.models import User, Rating

# Register your models here.
admin.site.register(User)
admin.site.register(Rating)
