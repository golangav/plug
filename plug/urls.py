
from django.conf.urls import url,include
from django.contrib import admin
from app01 import views
from yingun.service import v1

urlpatterns = [

    url(r'^yg/',v1.site.urls),
    url(r'^test/',views.test)

]
