from . import views
from django.urls import path
from .admin.registry import admin


urlpatterns = [
    path('',views.index)
]

urlpatterns.extend(admin.urls)