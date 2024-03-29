from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from event.models import Event, EventParticipant
from event.permissions import (IsModeratorOrRead, IsNotModerator,
                               IsOwnerOrModeratorOrCreate, PermissionForReview)
from event.serializers import (EventModeratorSerializer, EventSerializer,
                               ReviewSerializer, UserSerializer)
from event.utils import send_email

User = get_user_model()


class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsOwnerOrModeratorOrCreate,)


class EventViewSet(ModelViewSet):
    queryset = Event.objects.all()
    permission_classes = (IsModeratorOrRead,)
    filterset_fields = ["title", "start_at", "description", "address", "type"]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_serializer_class(self, *args, **kwargs):
        if "pk" in self.kwargs:
            event = get_object_or_404(Event, id=self.kwargs["pk"])
            if self.request.user == event.user:
                return EventModeratorSerializer
        return EventSerializer


@api_view(["GET"])
@permission_classes([IsNotModerator])
def get_users_events(request):
    events_id = EventParticipant.objects.filter(user=request.user).values_list(
        "event", flat=True
    )
    events = Event.objects.filter(id__in=events_id)
    serializer = EventSerializer(events, many=True)
    return Response(serializer.data)


class ReviewViewSet(ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = (PermissionForReview,)

    def get_queryset(self):
        event = get_object_or_404(Event, id=self.kwargs.get("event_id"))
        return event.reviews.all()

    def perform_create(self, serializer):
        event = get_object_or_404(Event, id=self.kwargs.get("event_id"))
        serializer.save(event=event, author=self.request.user)
        send_email(event, self.request.user.email, review=True)


@api_view(["POST"])
@permission_classes([IsNotModerator])
def get_registration_to_event(request, event_id):
    if EventParticipant.objects.filter(user=request.user, event=event_id).exists():
        event = EventParticipant.objects.get(user=request.user, event=event_id)
        event.delete()
        return Response(
            {"status": "Заявка на участие в мероприятии удалена"},
            status=status.HTTP_200_OK,
        )
    else:
        event = get_object_or_404(Event, id=event_id)
        EventParticipant.objects.create(event=event, user=request.user)
        send_email(event, request.user.email)
        return Response(
            {"status": "Заявка на участие в мероприятии создана"},
            status=status.HTTP_200_OK,
        )
