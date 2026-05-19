from django.urls import path
from catalog.apps import NewappConfig

app_name = NewappConfig.name

urlpatterns = [
    path('',)
]
