from rest_framework.generics import get_object_or_404
from rest_framework.permissions import BasePermission

from event.models import Review, User


class IsOwnerOrModeratorOrCreate(BasePermission):
    """
    Любой может зарегистрировать нового пользователя
    Модератор может  просматривать/изменять любую информацию о пользователях
    Не модератор может просматривать информацию только о себе, изменять любые
    свои данные, кроме поля "модератор"

    """

    def has_permission(self, request, view):
        if request.method == "POST":
            return True
        if not request.user or not request.user.is_authenticated:
            return False
        if request.user.is_moderator:
            return True
        if "pk" in view.kwargs:
            user = get_object_or_404(User, pk=view.kwargs["pk"])
            if "is_moderator" not in request.data:
                return request.user == user
        return False


class IsModeratorOrRead(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.is_moderator
            or request.method == "GET"
        )


class IsNotModerator(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and not request.user.is_moderator
        )


class PermissionForReview(BasePermission):
    """
    Любой может прочитать отзывы
    Оставить отзыв может только не модератор
    Изменить можно только свой собственный отзыв
    """

    def has_permission(self, request, view):
        if request.method == "GET":
            return True
        if not request.user or not request.user.is_authenticated:
            return False
        if "pk" in view.kwargs:
            review = get_object_or_404(Review, id=view.kwargs["pk"])
            return request.user == review.author
        return not request.user.is_moderator
