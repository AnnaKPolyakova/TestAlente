from django.contrib import admin
from django.contrib.admin import register
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group

from django.utils.translation import gettext_lazy as _
from event.models import Event, EventParticipant, User, Review


class UserAdmin(UserAdmin):

    list_display = (
        "username",
        "is_active",
        "is_staff",
        "is_superuser",
        "is_moderator",
    )
    list_filter = (
        "username",
        "is_active",
        "is_staff",
        "is_superuser",
        "is_moderator",
    )
    fieldsets = (
        (None, {"fields": ("username", "email", "password")}),
        (_("Personal info"), {"fields": ("first_name", "last_name")}),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "is_moderator"
                ),
            },
        ),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )


class EventParticipantInline(admin.TabularInline):
    model = EventParticipant
    extra = 0
    verbose_name_plural = "Список участников"


@register(Event)
class EventAdmin(admin.ModelAdmin):
    inlines = [
        EventParticipantInline,
    ]
    list_display = (
        "user",
        "title",
        "address",
        "description",
        "start_at",
    )
    list_filter = (
        "start_at",
        "user",
    )
    search_fields = ("title",)


@register(Review)
class EventAdmin(admin.ModelAdmin):
    list_display = (
        "text",
        "author",
        "event",
        "file",
        "pub_date",
    )
    list_filter = (
        "event",
        "author",
    )
    search_fields = ("title",)


admin.site.register(User, UserAdmin)
admin.site.unregister(Group)

