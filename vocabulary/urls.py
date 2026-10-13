from django.urls import path

from . import views

urlpatterns = [
    path("", views.word_list, name="word_list"),
    path("words/add/", views.word_create, name="word_create"),
    path("words/<int:pk>/", views.word_detail, name="word_detail"),
    path("words/<int:pk>/edit/", views.word_update, name="word_update"),
    path("words/<int:pk>/delete/", views.word_delete, name="word_delete"),
    path("words/<int:pk>/reviews/add/", views.review_create, name="review_create"),
    path("reviews/", views.review_list, name="review_list"),
    path("reviews/<int:pk>/delete/", views.review_delete, name="review_delete"),
]
