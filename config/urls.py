from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from books.views import (
    login_view, post_list, register_view, logout_view,
    post_create, post_update, post_delete, post_detail,
    forgot_password_view, restore_password_view,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path("books/", include("books.urls")),
    path("posts/", post_list, name="post-list"),
    path("posts/<int:pk>/", post_detail, name="post-detail"),
    path("posts/create/", post_create, name="post-create"),
    path("posts/<int:pk>/edit/", post_update, name="post-update"),
    path("posts/<int:pk>/delete/", post_delete, name="post-delete"),
    path("register/", register_view, name="register"),
    path("login/", login_view, name="login"),
    path("logout/", logout_view, name="logout"),
    path("forgot-password/", forgot_password_view, name="forgot-password"),
    path("restore-password/", restore_password_view, name="restore-password"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
