import json
from datetime import datetime
from typing import List, Optional
from abc import abstractmethod, ABCMeta

import requests

from weather.dto import WeatherTodayDTO, WeatherTimeInfoDTO, CountryServiceDTO, WikiServiceDTO, CountryDTO
from weather.exceptions import ResponseException, ServerReturnInvalidResponse, ResponseEmptyException, \
    NoAvailableServiceError


class WeatherTodayService:
    _WEATHER_API_ROOT_URL = 'https://api.openweathermap.org/data/2.5/weather?q={city}&' \
                            'appid={api_key}&units=metric'

    def __init__(self):
        self._city = None
        self._api_key = None
        self._response_json = None
        self._status_code = None

    def get_weather(self, city: str, api_key: str) -> WeatherTodayDTO:
        self._city = city
        self._api_key = api_key
        self._get_response()
        self._validate_response_or_raise()
        weather_dto = self._parse_response_json()
        return weather_dto

    def _get_response(self) -> None:
        url = self._WEATHER_API_ROOT_URL.format(city=self._city, api_key=self._api_key)
        response = requests.get(url)
        self._response_json = response.json()
        self._status_code = response.status_code

    def _validate_response_or_raise(self):
        if self._status_code != 200:
            raise ResponseException(self._response_json['message'])

    def _parse_response_json(self) -> WeatherTodayDTO:
        city = self._response_json['name']
        condition = self._response_json['weather'][0]['main']
        temperature = int(self._response_json['main']['temp'])
        wind_speed = round(self._response_json['wind']['speed'], 1)
        humidity = self._response_json['main']['humidity']
        icon = self._response_json['weather'][0]['icon']
        time_info = WeatherTimeInfoDTO(
            current=datetime.fromtimestamp(self._response_json['dt']).strftime('%H:%M'),
            sunrise=datetime.utcfromtimestamp(
                self._response_json['sys']['sunrise'] + self._response_json['timezone']).strftime('%H:%M'),
            sunset=datetime.utcfromtimestamp(
                self._response_json['sys']['sunset'] + self._response_json['timezone']).strftime('%H:%M')
        )
        lat = self._response_json['coord']['lat']
        lon = self._response_json['coord']['lon']
        weather_dto = WeatherTodayDTO(
            city=city,
            condition=condition,
            temperature=temperature,
            wind_speed=wind_speed,
            humidity=humidity,
            icon=icon,
            time_info=time_info,
            lat=lat,
            lon=lon)
        return weather_dto


class CountryServiceInterface(metaclass=ABCMeta):
    @abstractmethod
    def get_country_by_code(self, code: str, api_key: Optional[str]) -> CountryServiceDTO:
        pass


class WikiServiceInterface(metaclass=ABCMeta):
    @abstractmethod
    def get_wiki_page(self, query: str) -> WikiServiceDTO:
        pass


class RestcountriesService(CountryServiceInterface):
    _COUNTRY_API_CODE_URL = 'https://restcountries.com/v3.1/alpha/{code}'

    def __init__(self):
        self._code = None
        self._response_json = None
        self._status_code = None

    def get_country_by_code(self, code: str, api_key=None) -> CountryServiceDTO:
        self._code = code
        self._get_response()
        self._validate_response_or_raise()
        return self._parse_response_json()

    def _get_response(self) -> None:
        url = self._COUNTRY_API_CODE_URL.format(code=self._code)

        try:
            response = requests.get(url, timeout=(2, 2))
            self._status_code = response.status_code
            self._response_json = response.json()
        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError):
            self._status_code = 500
            self._response_json = None
        except json.JSONDecodeError:
            self._response_json = None

    def _validate_response_or_raise(self) -> None:
        if self._status_code != 200:
            if self._response_json is None:
                raise ServerReturnInvalidResponse(f'Server return status code {self._status_code}')
            raise ResponseException(self._response_json['message'])

    def _parse_response_json(self) -> CountryServiceDTO:
        name = self._response_json[0]['name']['common']
        code = self._response_json[0]['cca2']
        capital = self._response_json[0]['capital'][0]
        population = self._response_json[0]['population']
        country_dto = CountryServiceDTO(name=name,
                                        code=code,
                                        capital=capital,
                                        population=population)
        return country_dto


class GeonamesService(CountryServiceInterface):
    _COUNTRY_API_CODE_URL = 'http://api.geonames.org/countryInfoJSON?country={code}&username={api_key}'

    def __init__(self):
        self._code = None
        self._response_json = None
        self._status_code = None
        self._api_key = None

    def get_country_by_code(self, code: str, api_key: str) -> CountryServiceDTO:
        self._code = code
        self._api_key = api_key
        self._get_response()
        self._validate_response_or_raise()
        return self._parse_response_json()

    def _get_response(self) -> None:
        url = self._COUNTRY_API_CODE_URL.format(code=self._code, api_key=self._api_key)

        try:
            response = requests.get(url, timeout=(2, 2))
            self._status_code = response.status_code
            self._response_json = response.json()
        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError):
            self._status_code = 500
            self._response_json = None
        except json.JSONDecodeError:
            self._response_json = None

    def _validate_response_or_raise(self) -> None:
        if self._response_json is None:
            raise ServerReturnInvalidResponse(f'Server return invalid response')
        if not self._response_json['geonames']:
            raise ResponseEmptyException('Server return empty response')

    def _parse_response_json(self) -> CountryServiceDTO:
        name = self._response_json['geonames'][0]['countryName']
        code = self._response_json['geonames'][0]['countryCode']
        capital = self._response_json['geonames'][0]['capital']
        population = int(self._response_json['geonames'][0]['population'])
        country_dto = CountryServiceDTO(name=name,
                                        code=code,
                                        capital=capital,
                                        population=population)
        return country_dto


class FallbackCountryFacade:
    def __init__(self, services: List[CountryServiceInterface]):
        self._services = services

    def get_country_by_code(self, code: str, api_key: str) -> CountryServiceDTO:
        for service in self._services:
            try:
                return service.get_country_by_code(code, api_key)
            except (ServerReturnInvalidResponse, ResponseEmptyException, ResponseException):
                continue
        raise NoAvailableServiceError('No service are currently available to handle the request.')


class WikiService(WikiServiceInterface):
    _WIKI_API_URL = 'http://en.wikipedia.org/w/api.php?action=query&titles={query}' \
                    '&prop=extracts|pageimages&format=json&pithumbsize=1000'

    def __init__(self):
        self._query = None
        self._response_json = None
        self._status_code = None

    def get_wiki_page(self, query: str) -> WikiServiceDTO:
        self._query = query
        self._get_response()
        self._validate_response_or_raise()
        return self._parse_response_json()

    def _get_response(self) -> None:
        url = self._WIKI_API_URL.format(query=self._query)

        try:
            response = requests.get(url, timeout=(2, 2))
            self._status_code = response.status_code
            self._response_json = response.json()
        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError):
            self._status_code = 500
            self._response_json = None
        except json.JSONDecodeError:
            self._response_json = None

    def _parse_response_json(self) -> WikiServiceDTO:
        pages = self._response_json['query']['pages']
        _, page_info = next(iter(pages.items()))
        description = page_info['extract']
        image = page_info['thumbnail']['source'] if 'thumbnail' in page_info else ''
        return WikiServiceDTO(description=description, image=image)

    def _validate_response_or_raise(self) -> None:
        if self._response_json is None:
            raise ServerReturnInvalidResponse(f'Server return invalid response')
        if '-1' in self._response_json['query']['pages']:
            raise ResponseEmptyException('Server return empty response')


class CountryFacade:
    def __init__(self, country_services: List[CountryServiceInterface], wiki_service: WikiServiceInterface):
        self._country_services = country_services
        self._wiki_service = wiki_service
        self._errors = None

    def get_country_data(self, code: str, api_key: str) -> Optional[CountryDTO]:
        fallback_country_service = FallbackCountryFacade(self._country_services)
        try:
            country_data = fallback_country_service.get_country_by_code(code=code, api_key=api_key)
        except NoAvailableServiceError as error:
            self._errors = str(error)
            return None

        try:
            wiki_data = self._wiki_service.get_wiki_page(country_data.name)
        except (ServerReturnInvalidResponse, ResponseEmptyException) as error:
            self._errors = str(error)
            return None

        country_dto = CountryDTO(
            name=country_data.name,
            code=country_data.code,
            capital=country_data.capital,
            population=country_data.population,
            description=wiki_data.description,
            image=wiki_data.image)
        return country_dto

    def is_valid(self) -> bool:
        return self._errors is None

    def get_errors(self):
        return self._errors

# country_facade = CountryFacade(country_services=[GeonamesService()], wiki_service=WikiService())
# country_dto = country_facade.get_country_data()
#
# if not country_facade.is_valid():
#     print(country_facade.get_errors())
# else:
#     print(country_dto)
