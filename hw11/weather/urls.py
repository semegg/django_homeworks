from django.urls import path

from weather import views


app_name = 'weather'


urlpatterns = [
    path('today/', views.CityWeatherView.as_view(), name='today'),
    path('user/city/create/', views.UserCityCreateView.as_view(), name='user_city_create'),
    path('user/city/list/', views.UserCityListView.as_view(), name='user_city_list'),
    path('user/city/delete/', views.UserCityBulkDeleteView.as_view(), name='user_city_delete'),
    path('user/city_detail/<str:city>/', views.UserCityDetailView.as_view(), name='city_detail'),
    path('user/country_detail/<str:country>/', views.UserCountryDetailView.as_view(), name='country_detail'),
]
