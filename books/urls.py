from django.urls import path
from . import views
from books.views import logout_view

app_name = "books"

urlpatterns = [
    path("", views.BookListView.as_view(), name="list"),
    path("create/", views.BookCreateView.as_view(), name="create"),
    path("<int:pk>/edit/", views.BookUpdateView.as_view(), name = "edit"),
    path("<int:pk>/update/", views.BookUpdateView.as_view(), name="update"),
    path("<int:pk>/delete/", views.BookDeleteView.as_view() , name="delete"),
    path("logout/", logout_view, name="logout"),
    ]