
from django.contrib import admin
from django.urls import path, include, re_path
from django.views.generic import RedirectView
from django.conf import settings
from django.conf.urls.static import static
from .views_home import home


urlpatterns = [
    re_path(r'^admin$', RedirectView.as_view(url='/admin/', permanent=True)),
    path('', home),
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
]

# Servir archivos media en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)