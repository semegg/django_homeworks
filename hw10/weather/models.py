from typing import Optional

from django.contrib.auth import get_user_model
from django.db import models

from weather.dto import WikiServiceDTO
from weather.exceptions import ServerReturnInvalidResponse, ResponseEmptyException
from weather.services import WikiServiceInterface

User = get_user_model()


class Country(models.Model):
    name = models.CharField(max_length=128, unique=True, db_index=True)
    slug = models.SlugField(max_length=128, unique=True)
    code = models.CharField(max_length=3)
    population = models.IntegerField()
    description = models.TextField()
    flag = models.URLField(max_length=255)
    capital = models.CharField(max_length=200, unique=True)

    objects = models.Manager()

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('name',)
        verbose_name_plural = 'Countries'


class City(models.Model):
    name = models.CharField(max_length=128, unique=True, db_index=True)
    slug = models.SlugField(max_length=128, unique=True)
    description = models.TextField()
    image = models.URLField(max_length=255)
    lat = models.FloatField(verbose_name='latitude')
    lon = models.FloatField(verbose_name='longitude')
    country = models.ForeignKey(Country, on_delete=models.PROTECT, related_name='cities')

    objects = models.Manager()

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('name',)
        verbose_name_plural = 'Cities'
        unique_together = ('lon', 'lat')


class UserCity(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cities')
    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name='users')
    created = models.DateTimeField(auto_now_add=True)

    objects = models.Manager()

    def __str__(self):
        return f'{self.user} - {self.city}'

    class Meta:
        unique_together = ('user', 'city')
        verbose_name_plural = 'User cities'

class UserCountry(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='users')
    country = models.ForeignKey(City, on_delete=models.CASCADE, related_name='countries')
    created = models.DateTimeField(auto_now_add=True)

    objects = models.Manager()

    def __str__(self):
        return f'{self.user} - {self.country}'

    class Meta:
        unique_together = ('user', 'country')
        verbose_name_plural = 'User countries'

