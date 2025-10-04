"""
URL configuration for Green Vision project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    path('api/', include('api.urls')),
]

# Serve static and media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    # Serve from STATICFILES_DIRS instead of STATIC_ROOT
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns
    urlpatterns += staticfiles_urlpatterns()

# Admin site customization
admin.site.site_header = "Green Vision Admin"
admin.site.site_title = "Green Vision Admin Portal"
admin.site.index_title = "Welcome to Green Vision Administration"
