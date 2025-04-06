from django.urls import path
from . import views

# Empty URL patterns - face recognition has been disabled
urlpatterns = [
    path('dummy/', views.dummy_view, name='dummy_view'),
]
