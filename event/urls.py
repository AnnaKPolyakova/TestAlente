from django.urls import include, path
from rest_framework import routers

from .views import (EventViewSet, ReviewViewSet, UserViewSet,
                    get_registration_to_event, get_users_events)

router = routers.DefaultRouter()
router.register(r"auth/user", UserViewSet, basename="user")
router.register(r"event", EventViewSet)
router.register(r"event/(?P<event_id>\d+)/reviews", ReviewViewSet, basename="reviews")


extra_patterns = [
    path("", include(router.urls)),
    path("my_events/", get_users_events, name="my_events"),
    path(
        "event_registration/<int:event_id>/",
        get_registration_to_event,
        name="event_registration",
    ),
]

urlpatterns = [
    path("v1/", include(extra_patterns)),
]
