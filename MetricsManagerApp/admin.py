from django.contrib import admin

from .models import *

admin.site.register(UploadedFile)
admin.site.register(Company)

@admin.register(Industry)
class IndustryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')  # Customize based on your Industry model fields
    search_fields = ('name',)  # Add search functionality for name

@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'state')
    search_fields = ('name', 'state__name')  # Assuming you have a related field
    list_filter = ('state',)

@admin.register(State)
class StateAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'country')
    search_fields = ('name', 'country__name')  # Assuming you have a related field
    list_filter = ('country',)

@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)