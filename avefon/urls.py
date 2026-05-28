from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

admin.site.site_header  = "Avefon Trade Ltd — Admin"
admin.site.site_title   = "Avefon Admin"
admin.site.index_title  = "Avefon Trade Ltd Dashboard"

urlpatterns = [
    path('django-admin/', admin.site.urls),
    path('', include('frontend.urls')),
    path('', include('backend.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
