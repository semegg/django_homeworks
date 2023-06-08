from django.urls import path

from blog import views


app_name = 'blog'


urlpatterns = [
    path('', views.post_list, name='post_list'),
    path('category/<slug:category>', views.post_category, name='post_category'),
    path('search/', views.search_post, name='search_posts'),
    path('<int:year>/<int:month>/<int:day>/<slug:post_slug>/', views.post_detail, name='post_detail'),
    path('post/create/', views.add_post, name='add_post'),
    path('post/<int:post_id>/update/', views.update_post, name='update_post'),
    path('post/<int:post_id>/delete/', views.delete_post, name='delete_post'),
    path('post/<int:post_id>/like/', views.like_post, name='post_like'),
    path('post/<int:post_id>/dislike/', views.dislike_post, name='post_dislike'),
    path('post/<int:post_id>/add_comment/', views.add_comment, name='add_comment'),
    path('comment/<int:comment_id>/like/', views.like_comment, name='comment_like'),
    path('comment/<int:comment_id>/dislike/', views.dislike_comment, name='comment_dislike'),
    path('delete-comment/<int:comment_id>/', views.delete_comment, name='delete_comment'),
    path('toggle_comment_active/<int:comment_id>/', views.toggle_comment_active, name='toggle_comment_active'),
    path('post/<int:post_id>/follow', views.follow_or_unfollow,name = 'follow')
]

