from django.urls import path
from .api import book, cancel

urlpatterns = [
    path('book/', book, name='book'),
    path('cancel/', cancel, name='cancel'),
]