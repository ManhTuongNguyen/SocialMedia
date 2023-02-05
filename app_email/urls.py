from django.urls import path
from .views import *


app_name = 'app_email'
urlpatterns = [
    path('email/', SendEmail.as_view(), name='send_email'),
    path('feedback/', index_email, name='feedback')
]
