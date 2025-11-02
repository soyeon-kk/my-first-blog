from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from .models import Post
from rest_framework.response import Response
from .forms import PostForm
from rest_framework import viewsets, status
from .serializers import PostSerializer
from rest_framework.parsers import JSONParser, FormParser, MultiPartParser


# 글 목록
def post_list(request):
    posts = Post.objects.filter(published_date__lte=timezone.now()).order_by('published_date')
    return render(request, 'blog/post_list.html', {'posts': posts})


# 글 상세보기
def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    return render(request, 'blog/post_detail.html', {'post': post})


# 새 글 작성
def post_new(request):
    if request.method == "POST":
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.published_date = timezone.now()
            post.save()
            return redirect('post_detail', pk=post.pk)
    else:
        form = PostForm()
    # ✨ post=None을 넘겨서 템플릿의 {% if post %} 조건문이 정상 작동하게
    return render(request, 'blog/post_edit.html', {'form': form, 'post': None})


# 글 수정
def post_edit(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.method == "POST":
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.published_date = timezone.now()
            post.save()
            return redirect('post_detail', pk=post.pk)
    else:
        form = PostForm(instance=post)
    # ✨ post 객체를 같이 넘겨서 취소 버튼이 detail로 이동 가능
    return render(request, 'blog/post_edit.html', {'form': form, 'post': post})


# 글 삭제
def post_delete(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.method == "POST":
        post.delete()
        return redirect('post_list')
    return render(request, 'blog/post_confirm_delete.html', {'post': post})


# 테스트용 JS 페이지
def js_test(request):
    return render(request, 'blog/js_test.html')


class BlogImage(viewsets.ModelViewSet):
    queryset = Post.objects.all().order_by('-published_date')
    serializer_class = PostSerializer
    parser_classes = [JSONParser, FormParser, MultiPartParser]

    # ✅ Android multipart/form-data 대응
    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        data['author'] = request.user.id if request.user.is_authenticated else None
        data['created_date'] = timezone.now()
        data['published_date'] = timezone.now()

        serializer = self.get_serializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        print("❌ CREATE ERROR:", serializer.errors)  # PythonAnywhere 로그에서 디버깅용
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        data = request.data.copy()
        data['published_date'] = timezone.now()

        serializer = self.get_serializer(instance, data=data, partial=partial)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        print("❌ UPDATE ERROR:", serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)