from django.urls import path

from accounts import views


app_name = 'accounts'


urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('activate/<str:username>/<str:token>/', views.activate_account_view, name='activate'),
    path('reactivate-sent/', views.reactivation_sent_view, name='reactivate_sent'),
    path('password-reset-sent/', views.password_reset_sent_view, name='password_reset_sent'),
    path('password-reset-done/<str:username>/<str:token>/', views.password_reset_done_view, name='password_reset_done'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('create-profile/', views.profile_create_view, name='profile_create'),
    path('profile/<str:username>/update/', views.profile_update_view, name='profile_update'),
    path('profile/<str:username>/show/', views.profile_detail_view, name='profile_detail'),
    path('profile/<str:username>/follow/', views.follow_user_view, name='follow_user'),
    path('profile/<str:username>/unfollow/', views.unfollow_user_view, name='unfollow_user'),
    path('profile/<str:username>/show-followers/', views.show_followers_view, name='show_followers'),
    path('profile/<str:username>/show-followed/', views.show_followed_view, name='show_followed'),

]
