from django.conf import settings
from django.contrib import messages
from django.shortcuts import render, redirect
from django.utils.text import slugify
from django.views import View

from .forms import CityWeatherForm
from .models import City, UserCity
from .services import WeatherTodayService, ResponseException, WikiService


# from django.views.generic import DetailView, DeleteView, ListView, FormView, CreateView, UpdateView


class CityWeatherView(View):
    def get(self, request):
        form = CityWeatherForm()
        return render(request, 'weather/today.html', {'form': form})

    def post(self, request):
        form = CityWeatherForm(request.POST)
        weather = None

        if form.is_valid():
            api_key = settings.WEATHER_API_KEY
            city = form.clean_city()

            weather_service = WeatherTodayService()
            try:
                weather = weather_service.get_weather(city, api_key)
            except ResponseException as exception:
                messages.error(request, str(exception))
                return redirect('weather:today')

        form = CityWeatherForm()
        return render(request, 'weather/today.html', {'form': form, 'weather': weather})


class UserCityAddView(View):
    def post(self, request, city):
        user = request.user
        city = city
        print(city)
        api_key = settings.WEATHER_API_KEY

        weather_service = WeatherTodayService()
        wiki = WikiService()
        wiki = wiki.get_wiki_page(query=city)

        weather = weather_service.get_weather(city, api_key)
        city = City.objects.create(name=weather.city,
                                   slug=slugify(city),
                                   description=wiki.description,
                                   image=wiki.image,
                                   lat=weather.lat,
                                   lon=weather.lon, )
        add_city = UserCity.objects.create(user=user, city=city)
        if add_city:
            messages.success(request, f'{city.name} has been added')
            add_city.save()
        else:
            messages.error(request, 'Error')

            messages.error(request, 'Error')
        return render(request, 'weather/today.html')
