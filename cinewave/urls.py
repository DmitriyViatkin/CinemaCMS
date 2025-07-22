from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin

urlpatterns = [
    path('admin/', admin.site.urls),
    path('i18n/', include('django.conf.urls.i18n')),
]

urlpatterns += i18n_patterns(
    path('admins/', include('admins.urls')),
    path('', include('main.urls')),
    path('account/', include('authentication.urls')),
    path('user/', include('users.urls')),
    path('cinemas/', include('core.urls')),
    path('movies/', include('movie.urls')),
    path('celery-progress/', include('celery_progress.urls')),
    prefix_default_language=True,
)

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [path('__debug__/', include(debug_toolbar.urls))] + urlpatterns

    # Додаємо статичні та медіа шляхи *окремо*
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)