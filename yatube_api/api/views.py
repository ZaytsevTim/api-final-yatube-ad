from rest_framework import viewsets, permissions, filters
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.pagination import PageNumberPagination

from posts.models import Post, Group, Follow
from .serializers import (
    PostSerializer, GroupSerializer, CommentSerializer, FollowSerializer
)

User = get_user_model()


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all().order_by('-pub_date')
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    pagination_class = PageNumberPagination

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def perform_update(self, serializer):
        if serializer.instance.author != self.request.user:
            raise PermissionDenied('Изменение чужого контента запрещено!')
        serializer.save()

    def perform_destroy(self, instance):
        if instance.author != self.request.user:
            raise PermissionDenied('Удаление чужого контента запрещено!')
        instance.delete()


class GroupViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Group.objects.all().order_by('id')  # добавить order_by
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    pagination_class = None  # отключить пагинацию


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    pagination_class = None  

    def get_queryset(self):
        post_id = self.kwargs.get('post_id')
        post = get_object_or_404(Post, id=post_id)
        return post.comments.all().order_by('created')  # добавить order_by

    def get_queryset(self):
        post_id = self.kwargs.get('post_id')
        post = get_object_or_404(Post, id=post_id)
        return post.comments.all()

    def perform_create(self, serializer):
        post_id = self.kwargs.get('post_id')
        post = get_object_or_404(Post, id=post_id)
        serializer.save(author=self.request.user, post=post)

    def perform_update(self, serializer):
        if serializer.instance.author != self.request.user:
            raise PermissionDenied('Изменение чужого контента запрещено!')
        serializer.save()

    def perform_destroy(self, instance):
        if instance.author != self.request.user:
            raise PermissionDenied('Удаление чужого контента запрещено!')
        instance.delete()


class FollowViewSet(viewsets.ModelViewSet):
    serializer_class = FollowSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['following__username']
    pagination_class = None  # отключить пагинацию

    def get_queryset(self):
        return Follow.objects.filter(user=self.request.user).order_by('id')

    def perform_create(self, serializer):
        following_id = self.request.data.get('following')

        if not following_id:
            raise ValidationError({'following': 'Это поле обязательно.'})

        # Проверяем, передан ли ID или username
        try:
            # Пробуем найти по ID
            following = User.objects.get(id=following_id)
        except (ValueError, TypeError):
            # Если не число, пробуем найти по username
            try:
                following = User.objects.get(username=following_id)
            except User.DoesNotExist:
                raise ValidationError({'following': 'Пользователь не найден.'})

        if following == self.request.user:
            raise ValidationError(
                {'following': 'Нельзя подписаться на самого себя.'}
            )

        if Follow.objects.filter(
            user=self.request.user, following=following
        ).exists():
            raise ValidationError(
                {'following': 'Вы уже подписаны на этого пользователя.'}
            )

        serializer.save(user=self.request.user, following=following)
