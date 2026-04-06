from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.db.models import Q
from django.core.paginator import Paginator
from django.contrib.auth import login, logout
from django.contrib.auth.models import Group
from django.contrib.auth.decorators import permission_required
from functools import wraps
from books.forms import BookForm, LoginForm, RegisterForm, PostForm
from books.models import Book, Post
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
