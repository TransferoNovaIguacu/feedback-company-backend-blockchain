from django.urls import path
from .views import CompanyRegisterView

urlpatterns = [
    path("register/company/", CompanyRegisterView.as_view(), name="company_register"),
]

