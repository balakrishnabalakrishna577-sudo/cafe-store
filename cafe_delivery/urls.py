from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from cafe.admin import admin_site

urlpatterns = [
    # Custom Django Admin Panel (with Jazzmin styling)
    path('admin/', admin_site.urls),
    
    # REST API URLs
    path('api/v1/', include('api.urls')),
    
    # Main application URLs
    path('', include('cafe.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)