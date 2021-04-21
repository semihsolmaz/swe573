from django.urls import path
from tagpubDev import views

app_name = 'tagpubDev'

urlpatterns = [
    path('', views.index, name='index'),

]