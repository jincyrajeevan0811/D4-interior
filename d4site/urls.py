from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import include, path, re_path
from django.views.static import serve

from core.sitemaps import sitemaps
from core.views import robots_txt

admin.site.site_header = "D4 Interiors admin"
admin.site.site_title = "D4 Interiors admin"
admin.site.index_title = "Dashboard"

urlpatterns = [
    path("admin/", admin.site.urls),
    path("projects/", include("portfolio.urls")),
    path("", include("inquiries.urls")),
    path("", include("core.urls")),
    path("sitemap.xml", sitemap, {"sitemaps": sitemaps}, name="sitemap"),
    path("robots.txt", robots_txt, name="robots"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
elif settings.SERVE_MEDIA:
    # Simple hosting without a separate web server for uploads.
    urlpatterns += [re_path(r"^media/(?P<path>.*)$", serve, {"document_root": settings.MEDIA_ROOT})]

handler404 = "core.views.page_not_found"
