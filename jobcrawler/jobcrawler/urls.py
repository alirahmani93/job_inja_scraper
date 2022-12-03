from django.contrib import admin
from django.urls import path
from app.views import get_data
urlpatterns = [
    path('admin/', admin.site.urls),
    path('get-data/', get_data),
]
