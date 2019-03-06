from django.urls import path, include

from django.contrib import admin

admin.autodiscover()

from noteable import views

urlpatterns = [
	path('', views.home_page_action),
    path('noteable/', include('noteable.urls')),
]
