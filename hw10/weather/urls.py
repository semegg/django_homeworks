from django.urls import path

from weather import views


app_name = 'weather'


urlpatterns = [
    path('today/', views.CityWeatherView.as_view(), name='today'),
    path('user_city/<str:city>', views.UserCityAddView.as_view(), name='user_city_add'),
]

