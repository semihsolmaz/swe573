from django.urls import path
from tagpubDev import views

app_name = 'tagpubDev'

urlpatterns = [
    path('', views.index, name='index'),
    path('registration/', views.registration, name='registration'),
    path('articleDetail/<int:pk>', views.articleDetail, name='articleDetail'),
    path('registrationRequests/', views.registrationRequests, name='registrationRequests'),
    path('userLogin/', views.userLogin, name='userLogin'),
    path('tagList/', views.tagsList, name='tag_list'),
    path('userList/', views.userList, name='userList'),
    path('userProfile/', views.userProfile, name='userProfile'),
]
