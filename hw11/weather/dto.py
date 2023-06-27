from typing import NamedTuple


class WeatherTimeInfoDTO(NamedTuple):
    current: str
    sunrise: str
    sunset: str


class GeoCoordinatesDTO(NamedTuple):
    lon: float
    lat: float


class WeatherTodayDTO(NamedTuple):
    city: str
    country_code: str
    coordinates: GeoCoordinatesDTO
    condition: str
    temperature: int
    wind_speed: float
    humidity: int
    time_info: WeatherTimeInfoDTO
    icon: str


class CountryServiceDTO(NamedTuple):
    name: str
    code: str
    capital: str
    population: int


class WikiServiceDTO(NamedTuple):
    description: str
    image: str


class CountryDTO(NamedTuple):
    name: str
    code: str
    capital: str
    population: int
    description: str
    image: str
