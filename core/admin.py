from django.contrib import admin
from .models import Profile, Listing, ListingImage

admin.site.register(Profile)
admin.site.register(Listing)
admin.site.register(ListingImage)