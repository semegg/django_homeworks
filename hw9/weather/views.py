from django.contrib import messages
from django.shortcuts import render, redirect
from django.views import View
from django.conf import settings

from .forms import CityWeatherForm
from .services import WeatherTodayService, ResponseException


# from django.views.generic import DetailView, DeleteView, ListView, FormView, CreateView, UpdateView


class CityWeatherView(View):
    def get(self, request):
        form = CityWeatherForm()
        return render(request, 'weather/today.html', {'form': form})

    def post(self, request):
        form = CityWeatherForm(request.POST)
        weather = None
        forecast = None
        if form.is_valid():
            api_key = settings.WEATHER_API_KEY
            city = form.clean_city()

            weather_service = WeatherTodayService()
            try:
                weather = weather_service.get_weather(city, api_key)
                forecasts = weather_service.get_forecast(city, api_key)
            except ResponseException as exception:
                messages.error(request, str(exception))
                return redirect('weather:today')
        form = CityWeatherForm()
        return render(request, 'weather/today.html', {'form': form, 'weather': weather, 'forecasts': forecasts})

