from rest_framework import serializers
from .models import Post
from django.utils import timezone

class PostSerializer(serializers.ModelSerializer):
    author = serializers.CharField(read_only=True)
    created_date = serializers.DateTimeField(read_only=True)
    published_date = serializers.DateTimeField(read_only=True)

    # ✅ 다시 쓰기 가능한 필드로 (업로드 가능)
    image = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = Post
        fields = ['id', 'author', 'title', 'text', 'created_date', 'published_date', 'image']

    # (선택) 응답에서 이미지 URL을 조정하고 싶으면 to_representation으로 처리
    def to_representation(self, instance):
        data = super().to_representation(instance)
        url = data.get("image")
        if url:
            # DRF ImageField는 보통 '/media/...'를 돌려줌.
            # 에뮬레이터에서도 바로 쓰려면 절대 URL로 바꾸고 싶을 때 아래 사용:
            request = self.context.get('request')
            if request and url.startswith("/"):
                data["image"] = request.build_absolute_uri(url)  # 예: http://10.0.2.2:8000/media/...
        return data

    def create(self, validated_data):
        request = self.context.get('request')
        username = request.user.username if (request and request.user.is_authenticated) else "AnonymousUser"
        return Post.objects.create(
            author=username,
            created_date=timezone.now(),
            published_date=timezone.now(),
            **validated_data
        )

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.published_date = timezone.now()
        instance.save()
        return instance
