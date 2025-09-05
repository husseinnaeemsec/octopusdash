from . import views
from django.urls import path
from .admin.registry import admin


urlpatterns = [
    path('',views.DashboardView.as_view(),name='octopusdash-index'),
    path('login/',views.DashboardLoginView.as_view(),name='octopusdash-login'),
    path("logout/",views.logout_view,name='octopusdash-logout'),
    path("plugins/",views.PluginsView.as_view(),name='octopusdash-plugins')
]

urlpatterns.extend(admin.urls)