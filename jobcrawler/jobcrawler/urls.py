from django.contrib import admin
from django.urls import path
from app.views import get_data,get_detail_data
urlpatterns = [
    path('admin/', admin.site.urls),
    path('get-data/', get_data),
    path('get-detail-data/', get_detail_data),
]
