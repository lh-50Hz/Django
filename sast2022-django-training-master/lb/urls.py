from django.urls import path, include
from . import views

urlpatterns = [
    path('leaderboard/', views.leaderboard),
    # TODO: Config URL Patterns
    path('history/<str:username>/', views.history),
    path('submit/', views.submit),
    path('vote/', views.vote),
]
