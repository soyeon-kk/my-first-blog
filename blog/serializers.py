from rest_framework import serializers
from .models import Post
from django.utils import timezone

class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ['id', 'author', 'title', 'text', 'created_date', 'published_date', 'image']
        read_only_fields = ['author', 'created_date', 'published_date']

    # 새 글 등록 시 자동으로 날짜, author 설정
    def create(self, validated_data):
        request = self.context.get('request', None)
        validated_data['author'] = request.user if request and request.user.is_authenticated else None
        validated_data['created_date'] = timezone.now()
        validated_data['published_date'] = timezone.now()
        return Post.objects.create(**validated_data)

    # 수정 시 자동으로 날짜 갱신
    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.published_date = timezone.now()
        instance.save()
        return instance
