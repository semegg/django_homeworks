from datetime import datetime
from typing import NamedTuple

import requests


class WeatherTimeInfoDTO(NamedTuple):
    current: str
    sunrise: str
    sunset: str


class WeatherTodayDTO(NamedTuple):
    city: str
    condition: str
    temperature: int
    wind_speed: float
    humidity: int
    time_info: WeatherTimeInfoDTO
    icon: str


class WeatherForecastDTO(NamedTuple):
    temperature: int
    icon: str
    time: str


class ResponseException(Exception):
    pass


class WeatherTodayService:
    _WEATHER_API_ROOT_URL = 'https://api.openweathermap.org/data/2.5/weather?q={city}&' \
                            'appid={api_key}&units=metric'
    _FORECASTS_API_URL = 'http://api.openweathermap.org/data/2.5/forecast?q={city}&&units=metric&appid={api_key}'

    def __init__(self):
        self._city = None
        self._api_key = None
        self._response_json = None
        self._forecast_response_json = None
        self._status_code = None

    def _parse_forecast_response_json(self):
        context = []
        for data in self._forecast_response_json['list'][::5]:
            time = datetime.fromtimestamp(data['dt']).strftime('%H:%M')
            icon = data['weather'][0]['icon']
            temperature = round(data['main']['temp'])
            forecast = {'temperature': temperature, 'icon': icon, 'time': time}
            context.append(forecast)
        return context
    def get_weather(self, city: str, api_key: str) -> WeatherTodayDTO:
        self._city = city
        self._api_key = api_key
        self._get_response()
        self._validate_response_or_raise()
        weather_dto = self._parse_response_json()
        return weather_dto

    def get_forecast(self, city: str, api_key: str):
        self._city = city
        self._api_key = api_key
        self._get_forecast_response()
        self._validate_response_or_raise()
        forecast_info = self._parse_forecast_response_json()
        return forecast_info

    def _get_forecast_response(self) -> None:
        forecast_url = self._FORECASTS_API_URL.format(city=self._city, api_key=self._api_key)
        self._forecast_response_json = requests.get(forecast_url).json()
        self._parse_forecast_response_json()

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

        weather_dto = WeatherTodayDTO(
            city=city,
            condition=condition,
            temperature=temperature,
            wind_speed=wind_speed,
            humidity=humidity,
            icon=icon,
            time_info=time_info)
        return weather_dto


