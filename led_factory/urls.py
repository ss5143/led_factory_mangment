from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from .pwa import pwa_manifest, pwa_service_worker


urlpatterns = [
    path("manifest.json", pwa_manifest, name="pwa_manifest"),
    path("service-worker.js", pwa_service_worker, name="pwa_service_worker"),
    path("accounts/", include("allauth.urls")),
    path("admin/", admin.site.urls),

    path("", include("products.urls")),

    path("", include("orders.urls")),

    path("", include("purchases.urls")),

    path(
        "suppliers/",
        include("suppliers.urls")
    ),

    path(
        "customers/",
        include("customers.urls")
    ),

    path(
        "reports/",
        include("reports.urls")
    ),

    path(
        "",
        include("accounts.urls")
    ),
]


if settings.DEBUG:

    urlpatterns += static(
        settings.STATIC_URL,
        document_root=settings.BUNDLE_DIR / "static"
    )

    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )