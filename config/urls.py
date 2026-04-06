from django.contrib import admin
from django.urls import include, path
from books.views import login_view, post_list, register_view, logout_view, post_create, post_update, post_delete

urlpatterns = [
    path('admin/', admin.site.urls),
    path("books/", include("books.urls")),
    path("posts/", post_list, name="post-list"),
    path("posts/create/", post_create, name="post-create"),
    path("posts/<int:pk>/edit/", post_update, name="post-update"),
    path("posts/<int:pk>/delete/", post_delete, name="post-delete"),
    path("register/", register_view, name="register"),
    path("login/", login_view, name="login"),
    path("logout/", logout_view, name="logout"),
]
