from django.urls import path
from tagpubDev import views

app_name = 'tagpubDev'

urlpatterns = [
    path('', views.index, name='index'),
    path('registration/', views.registration, name='registration'),
    path('registrationRequests/', views.registrationRequests, name='registrationRequests'),
    path('user_login/', views.user_login, name='user_login'),
]
