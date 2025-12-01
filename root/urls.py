from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns

urlpatterns = [
    path('i18n/', include('django.conf.urls.i18n')),  # set_language
]

urlpatterns += i18n_patterns(
    path('admin/', admin.site.urls),
    path('', include('apps.urls')),     # BU YERGA i18n_patterns JOYLASHADI ❗
)

# static files
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
