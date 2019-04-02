from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings

from django.contrib import admin

admin.autodiscover()

from noteable import views

urlpatterns = [
	path('', views.home_page_action),
    path('noteable/', include('noteable.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
