from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.home_page_action, name='home'),
    path('login', views.login_action, name='login'),
    path('logout', views.logout_action, name='logout'),
    path('register', views.register_action, name='register'),
    path('logged_home', views.logged_home_action, name='logged_home'),
    path('play', views.play_action, name='play'),
    path('results', views.results_action, name='results'),
    path('account', views.account_action, name='account'),
]
