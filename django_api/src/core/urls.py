from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

urlpatterns = [
    path("admin/", admin.site.urls),


    # Schema OpenAPI (JSON)
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),

    # Swagger UI
    path(
        "api/docs/swagger/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),

    # Redoc (outra UI bonita)
    path(
        "api/docs/redoc/",
        SpectacularRedocView.as_view(url_name="schema"),
        name="redoc",
    ),

    # Aqui inclui as rotas de autenticação
    path("api/auth/", include("users.api_urls")),
]
