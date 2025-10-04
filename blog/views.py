from django.shortcuts import render

# Create your views here.
def post_list(request):
    return render(request, 'blog/post_list.html', {}) # blog/post_list.html 템플릿을 보여준다는 의미