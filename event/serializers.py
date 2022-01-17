from datetime import datetime

from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.generics import get_object_or_404

from event.models import Event, Review, EventParticipant

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        max_length=128, min_length=8, write_only=True
    )

    class Meta:
        model = User
        fields = ("id", "username", "email", "password", "moderator")

    def create(self, validated_data):
        user = super(UserSerializer, self).create(validated_data)
        user.set_password(validated_data["password"])
        user.save()
        return user


class EventSerializer(serializers.ModelSerializer):

    class Meta:
        model = Event
        fields = "__all__"
        read_only_fields = ["user"]


class EventModeratorSerializer(serializers.ModelSerializer):

    participant = serializers.SerializerMethodField()

    class Meta:
        model = Event
        fields = "__all__"
        read_only_fields = ["user"]

    def get_participant(self, obj):
        users_id = obj.event_participants.values_list('user', flat=True)
        users = User.objects.filter(id__in=users_id)
        return UserSerializer(users, many=True).data


class ReviewSerializer(serializers.ModelSerializer):

    class Meta:
        model = Review
        fields = "__all__"
        read_only_fields = ["author", "event"]

    def validate(self, data):
        if self.context['request'].method != 'POST':
            return data

        author = self.context['request'].user
        event_id = (
            self.context['request'].parser_context['kwargs']['event_id']
        )
        if Review.objects.filter(author=author, event=event_id).exists():
            raise serializers.ValidationError(
                "Вы уже оставили отзыв на данное событие"
            )
        event = get_object_or_404(Event, id=event_id)
        if not EventParticipant.objects.filter(event=event_id,
                                               user=author).exists():
            raise serializers.ValidationError(
                "Вы не были зарегистрированы на данное мероприятие"
            )
        if event.start_at.timestamp() >= datetime.now().timestamp():
            raise serializers.ValidationError(
                "Мероприятие еще не состоялось, рано оставлять отзыв"
            )
        return data
