# blog/views.py
from functools import wraps

from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone

from .forms import PostForm
from .models import Post, SecurityKey

from rest_framework import viewsets
from rest_framework.parsers import JSONParser, FormParser, MultiPartParser
from .serializers import PostSerializer


# -------------------------
#   간단한 관리자 인증 데코레이터
# -------------------------
def admin_required(view_func):
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if not request.session.get("is_admin_authenticated", False):
            return redirect("admin_login")
        return view_func(request, *args, **kwargs)

    return _wrapped


# -------------------------
#   관리자 보안키 로그인 / 로그아웃
# -------------------------
def admin_login(request):
    if request.method == "POST":
        key = request.POST.get("security_key", "").strip()

        if SecurityKey.objects.filter(secret=key).exists():
            # 세션에 플래그 저장
            request.session["is_admin_authenticated"] = True
            messages.success(request, "관리자 모드로 로그인되었습니다.")
            return redirect("post_list")
        else:
            messages.error(request, "보안키가 올바르지 않습니다.")

    return render(request, "blog/admin_login.html")


def admin_logout(request):
    # 세션 플래그 제거
    request.session.pop("is_admin_authenticated", None)
    messages.info(request, "로그아웃 되었습니다.")
    return redirect("admin_login")


# -------------------------
#   HTML 템플릿(관리자용) 뷰
# -------------------------
@admin_required
def post_list(request):
    posts = (
        Post.objects.filter(published_date__lte=timezone.now())
        .order_by("-published_date")
    )
    return render(request, "blog/post_list.html", {"posts": posts})


@admin_required
def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    return render(request, "blog/post_detail.html", {"post": post})


@admin_required
def post_new(request):
    if request.method == "POST":
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.published_date = timezone.now()
            post.save()
            return redirect("post_detail", pk=post.pk)
    else:
        form = PostForm()

    return render(request, "blog/post_edit.html", {"form": form, "post": None})


@admin_required
def post_edit(request, pk):
    post = get_object_or_404(Post, pk=pk)

    if request.method == "POST":
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.published_date = timezone.now()
            post.save()
            return redirect("post_detail", pk=post.pk)
    else:
        form = PostForm(instance=post)

    return render(request, "blog/post_edit.html", {"form": form, "post": post})


@admin_required
def post_delete(request, pk):
    post = get_object_or_404(Post, pk=pk)

    if request.method == "POST":
        post.delete()
        return redirect("post_list")

    return render(request, "blog/post_confirm_delete.html", {"post": post})


@admin_required
def js_test(request):
    return render(request, "blog/js_test.html")


# -------------------------
#   DRF API (클라이언트 앱용)
#   -> 여기는 계속 공개 (앱에서 조회)
# -------------------------
class BlogImage(viewsets.ModelViewSet):
    queryset = Post.objects.all().order_by("-published_date")
    serializer_class = PostSerializer
    parser_classes = [JSONParser, FormParser, MultiPartParser]
