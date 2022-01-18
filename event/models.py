from datetime import datetime

from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

from event.validators import data_time_validator


class UserManager(BaseUserManager):

    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError("The given email must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault("is_moderator", True)
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):

    objects = UserManager()

    is_moderator = models.BooleanField(
        default=False, verbose_name="Модератор", help_text="Выберите роль"
    )

    class Meta:
        verbose_name = "Профайл"
        verbose_name_plural = "Профайлы"

    def __str__(self):
        return self.username


class Event(models.Model):
    class TYPE(models.TextChoices):
        EMAIL = "REGIONAL", _("Региональное")
        MAIN = "LOCAL", _("Локальное")

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="event",
        verbose_name="Автор",
    )
    title = models.CharField(
        max_length=40,
        verbose_name="Название",
        help_text="Не более 40 символов",
    )
    type = models.CharField(
        choices=TYPE.choices,
        max_length=40,
        verbose_name="Выбор типа мероприятия",
    )
    address = models.CharField(max_length=200, verbose_name="Адрес")
    description = models.TextField(verbose_name="Дополнительная информация")
    start_at = models.DateTimeField(
        verbose_name="Начало", validators=[data_time_validator]
    )

    class Meta:
        ordering = ("start_at",)
        verbose_name = "Мероприятие"
        verbose_name_plural = "Мероприятия"

    def __str__(self):
        return self.title


class EventParticipant(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="event_participants",
        null=True,
        verbose_name="Участник",
    )
    event = models.ForeignKey(
        Event,
        on_delete=models.RESTRICT,
        related_name="event_participants",
        verbose_name="Мероприятие",
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["user", "event"], name="unique_participant")
        ]
        ordering = ["-event"]
        verbose_name = "Участник"
        verbose_name_plural = "Участники"

    def __str__(self):
        return f"Участник @{self.user.username}, " f"мероприятие: {self.event.title}"


class Review(models.Model):
    text = models.TextField(
        verbose_name="Текст отзыва",
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="reviews", verbose_name="Автор"
    )
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name="reviews",
        verbose_name="Мероприятие",
    )
    file = models.FileField(
        blank=True,
        upload_to="reviews/",
        verbose_name="Файл",
    )
    pub_date = models.DateTimeField(
        verbose_name="Дата публикации отзыва", db_index=True, auto_now_add=True
    )

    def __str__(self):
        return self.text

    class Meta:
        ordering = ["-pub_date"]
        constraints = [
            models.UniqueConstraint(fields=["author", "event"], name="unique_review"),
        ]
        verbose_name = "Отзыв"
        verbose_name_plural = "Отзывы"
