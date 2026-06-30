from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

from apps.system.views import backend_index

urlpatterns = [
    path("", backend_index, name="backend-index"),
    path("admin/", admin.site.urls),
    path("api/accounts/", include("apps.accounts.urls")),
    path("api/portal/", include("apps.portal.urls")),
    path("api/members/", include("apps.members.urls")),
    path("api/news/", include("apps.news.urls")),
    path("api/publications/", include("apps.publications.urls")),
    path("api/documents/", include("apps.documents.urls")),
    path("api/instruments/", include("apps.instruments.urls")),
    path("api/students/", include("apps.students.urls")),
    path("api/cms/", include("apps.system.cms_urls")),
    path("api/", include("apps.system.urls")),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("swagger/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


