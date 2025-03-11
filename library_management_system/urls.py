from django.contrib import admin # type: ignore
from django.urls import path, include# type: ignore


urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('', include('library.urls')),
    
]

