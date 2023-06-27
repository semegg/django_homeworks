from django.contrib import admin

from .models import Country, City, UserCity


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'capital', 'flag')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ('name',  'image', 'lat', 'lon')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}



@admin.register(UserCity)
class UserCity(admin.ModelAdmin):
    list_display = ('user', 'city')
    search_fields = ('city', 'user')
    list_filter = ('user', 'city')
