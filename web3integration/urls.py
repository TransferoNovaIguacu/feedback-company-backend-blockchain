from django.urls import include, path
from .views import InitialView

urlpatterns = [
    path("", InitialView.as_view()),
    path('api/v1/', include('tokens.urls')),
]