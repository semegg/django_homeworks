from urllib.parse import urlencode

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.text import slugify
from django.views import View
from django.views.generic import ListView

from .forms import CityWeatherForm
from .models import Country, City, UserCity
from .services import WeatherTodayService, ResponseException, CountryFacade, RestcountriesService, GeonamesService, \
    WikiService, WikiFacade


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


class UserCityCreateView(LoginRequiredMixin, View):
    def post(self, request):
        user = request.user
        api_key = settings.COUNTRY_API_KEY

        city = request.POST.get('city')
        country_code = request.POST.get('country_code')
        lon = float(request.POST.get('lon'))
        lat = float(request.POST.get('lat'))

        country = self._get_country_or_create(country_code, api_key)
        if country is None:
            messages.error(request, 'Something went wrong with get country data')
            return redirect('weather:today')

        city = self._get_city_or_create(city_name=city, country=country, lon=lon, lat=lat)
        if city is None:
            messages.error(request, 'Something went wrong with get city data')
            return redirect('weather:today')

        if self._check_user_city_exists(user=user, city=city):
            messages.warning(request, f'City {city.name} is already in your list')
            return redirect('weather:today')

        self._create_user_city(user=user, city=city)
        messages.success(request, f'Country {country.name} and city {city.name} successfully added')
        return redirect('weather:today')

    def _get_country_or_create(self, country_code, api_key):
        country = Country.objects.filter(code=country_code).first()
        if country is not None:
            return country

        country_facade = CountryFacade(country_services=[RestcountriesService(), GeonamesService()],
                                       wiki_service=WikiService())
        country_dto = country_facade.get_country_data(api_key=api_key, code=country_code)

        if not country_facade.is_valid():
            return None

        country = Country.objects.filter(name=country_dto.name).first()
        if country is not None:
            return country

        country = Country.objects.create(name=country_dto.name,
                                         slug=slugify(country_dto.name),
                                         code=country_dto.code,
                                         population=country_dto.population,
                                         description=country_dto.description,
                                         flag=country_dto.image,
                                         capital=country_dto.capital)

        return country

    def _get_city_or_create(self, city_name, country, lon, lat):
        city = City.objects.filter(name=city_name).first()
        if city is not None:
            return city

        wiki_facade = WikiFacade(wiki_service=WikiService())
        wiki_dto = wiki_facade.get_page_data(city_name)

        if not wiki_facade.is_valid():
            return None

        city = City.objects.create(name=city_name,
                                   slug=slugify(city_name),
                                   description=wiki_dto.description,
                                   image=wiki_dto.image,
                                   lat=lat,
                                   lon=lon,
                                   country=country)
        return city

    def _check_user_city_exists(self, user, city):
        user_city = UserCity.objects.filter(user=user, city=city).exists()
        return user_city

    def _create_user_city(self, user, city):
        user_city = UserCity.objects.create(user=user, city=city)
        return user_city


class UserCityListView(LoginRequiredMixin, ListView):
    template_name = 'weather/city/user_city_list.html'
    context_object_name = 'user_cities'
    paginate_by = 2

    def get_queryset(self):
        queryset = UserCity.objects.filter(user=self.request.user)
        country = self.request.GET.get('country')
        if country:
            queryset = queryset.filter(city__country__name=country)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page'] = context.pop('page_obj', None)
        context['country'] = self.request.GET.get('country')

        query_params = self.request.GET.copy()
        query_params.pop('page', None)
        query_string = urlencode(query_params)

        if query_string:
            query_string = '&' + query_string

        context['query_string'] = query_string
        return context


class UserCityBulkDeleteView(LoginRequiredMixin, View):
    def post(self, request):
        user_city_ids = request.POST.getlist('selectors')
        if not user_city_ids:
            messages.warning(request, 'Nothing to delete')
            return redirect('weather:user_city_list')

        user_city_ids = map(int, user_city_ids)
        user_cities = UserCity.objects.filter(user=request.user, id__in=user_city_ids)

        message = 'Delete: '
        message += ', '.join([user_city.city.name for user_city in user_cities])
        messages.success(request, message)

        user_cities.delete()
        return redirect('weather:user_city_list')


class UserCityDetailView(LoginRequiredMixin, View):
    def get(self, request, city):
        template_name = 'weather/city/user_city_detail.html'
        city_info = City.objects.get(name=city)
        print(city_info.name)
        if city:
            return render(request,template_name , {'city_info': city_info})
        else:
            return render(request, 'error.html', {'error': '404'})


class UserCountryDetailView(LoginRequiredMixin, View):
    def get(self, request, country):
        template_name = 'weather/city/user_country_detail.html'
        country_info = Country.objects.get(name=country)
        print(country_info.name)
        if country_info:
            return render(request,template_name , {'country_info': country_info})
        else:
            return render(request, 'error.html', {'error': '404'})
