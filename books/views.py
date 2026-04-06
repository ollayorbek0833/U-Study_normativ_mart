from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.db.models import Q
from django.core.paginator import Paginator
from django.contrib.auth import login, logout
from django.contrib.auth.models import Group
from django.contrib.auth.decorators import permission_required
from functools import wraps
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.utils import timezone
from threading import Thread
from books.forms import BookForm, LoginForm, RegisterForm, PostForm, ForgotPasswordForm, RestorePasswordForm
from books.models import Book, Post, Code, generate_code, exp_time_now
from django.views.generic import ListView, CreateView, DeleteView, UpdateView
from django.utils.decorators import method_decorator


def login_required(func):
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect("login")
        return func(request, *args, **kwargs)
    return wrapper


class BookListView(ListView):
    model = Book
    template_name = "books/book_list.html"
    context_object_name = "books"
    ordering = ["created_at"]


@method_decorator(login_required, name="dispatch")
class BookCreateView(CreateView):
    model = Book
    template_name = "books/book_form.html"
    success_url = reverse_lazy("books:list")
    form_class = BookForm

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["mode"] = "create"
        return ctx


@method_decorator(login_required, name="dispatch")
class BookUpdateView(UpdateView):
    model = Book
    form_class = BookForm
    template_name = "books/book_form.html"
    success_url = reverse_lazy("books:list")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["mode"] = "update"
        return ctx


@method_decorator(login_required, name="dispatch")
class BookDeleteView(DeleteView):
    model = Book
    template_name = "books/book_confirm_delete.html"
    success_url = reverse_lazy("books:list")
    context_object_name = 'book'


def post_list(request):
    q = request.GET.get("q", "").strip()
    queryset = Post.objects.order_by("-created_at")
    if q:
        queryset = queryset.filter(
            Q(title__icontains=q) | Q(content__icontains=q)
        )
    paginator = Paginator(queryset, 5)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    return render(request, "books/post_list.html", {"posts": page_obj, "page_obj": page_obj, "q": q})


@login_required
@permission_required('books.add_post', login_url='/login/')
def post_create(request):
    if request.method == "POST":
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect("post-list")
    else:
        form = PostForm()
    return render(request, "books/post_form.html", {"form": form, "mode": "create"})


@login_required
@permission_required('books.change_post', login_url='/login/')
def post_update(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.method == "POST":
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            return redirect("post-list")
    else:
        form = PostForm(instance=post)
    return render(request, "books/post_form.html", {"form": form, "mode": "update"})


@login_required
@permission_required('books.delete_post', login_url='/login/')
def post_delete(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.method == "POST":
        post.delete()
        return redirect("post-list")
    return render(request, "books/post_confirm_delete.html", {"post": post})


def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    return render(request, "books/post_detail.html", {"post": post})


def register_view(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data["password"])
            user.save()
            user_group, _ = Group.objects.get_or_create(name="User")
            user.groups.add(user_group)
            return redirect("login")
    else:
        form = RegisterForm()
    return render(request, "books/register.html", {"form": form})


def login_view(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            user = form.cleaned_data["user"]
            login(request, user)
            return redirect("post-list")
    else:
        form = LoginForm()
    return render(request, "books/login.html", {"form": form})


def logout_view(request):
    logout(request)
    return redirect("login")


def send_email_thread(subject, message, recipient):
    thread = Thread(target=send_mail, args=(subject, message, 'noreply@example.com', [recipient]))
    thread.start()


def forgot_password_view(request):
    if request.method == "POST":
        form = ForgotPasswordForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                form.add_error("username", "User not found.")
                return render(request, "books/forgot_password.html", {"form": form})
            code = Code.objects.create(
                code=generate_code(),
                user=user,
                expired_date=exp_time_now(),
            )
            send_email_thread("Parolni tiklash", f"Code: {code.code}", user.email)
            request.session['reset_user_id'] = user.id
            return redirect("restore-password")
    else:
        form = ForgotPasswordForm()
    return render(request, "books/forgot_password.html", {"form": form})


def restore_password_view(request):
    if request.method == "POST":
        form = RestorePasswordForm(request.POST)
        if form.is_valid():
            code_value = form.cleaned_data["code"]
            new_password = form.cleaned_data["new_password"]
            user_id = request.session.get('reset_user_id')
            if not user_id:
                form.add_error(None, "Session expired. Try again.")
                return render(request, "books/restore_password.html", {"form": form})
            try:
                code_obj = Code.objects.filter(user_id=user_id, code=code_value).latest('expired_date')
            except Code.DoesNotExist:
                form.add_error("code", "Invalid code.")
                return render(request, "books/restore_password.html", {"form": form})
            if timezone.now() > code_obj.expired_date:
                form.add_error("code", "Code has expired.")
                return render(request, "books/restore_password.html", {"form": form})
            user = code_obj.user
            user.set_password(new_password)
            user.save()
            del request.session['reset_user_id']
            return redirect("login")
    else:
        form = RestorePasswordForm()
    return render(request, "books/restore_password.html", {"form": form})
