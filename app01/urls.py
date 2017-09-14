
from django.conf.urls import url
from app01 import views

urlpatterns = [
    url(r'^test/', views.test),
]
