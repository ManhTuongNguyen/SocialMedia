from django.urls import path
from . import views


app_name = 'core'
urlpatterns = [
    path('', views.index, name='index'),
    path('sign-up/', views.sign_up, name='sign_up'),
    path('sign-in/', views.sign_in, name='sign_in'),
    path('log-out/', views.log_out, name='log_out'),
    path('setting-general/', views.setting_general, name='setting-general'),
    path('setting-secure/', views.setting_secure, name='setting-secure'),
    path('forget-password/', views.forget_password, name='forget-password'),
    path('upload/', views.upload, name='upload'),
    path('like/', views.like_post, name='like_post'),
    path('profile/<str:pk>', views.profile, name='profile'),
    path('follow/', views.follow, name='follow'),
    path('search/', views.search, name='search'),
    path('post-details/<str:pk>/', views.PostDetails.as_view(), name='post_details'),
    path('post-comment/', views.post_comment, name='post_comment'),
    path('delete-post', views.DeletePost.as_view(), name='delete_post'),
    path('edit-post/', views.edit_post, name='edit_post'),
    path('edit-comment/', views.edit_comment, name='edit_comment'),
    path('delete-comment/', views.delete_comment, name='delete_comment')
]
