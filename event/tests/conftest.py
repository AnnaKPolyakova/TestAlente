import shutil
import tempfile

import pytest
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIClient

from event.models import Event, EventParticipant, Review

SMALL_GIF = (
    b"\x47\x49\x46\x38\x39\x61\x01\x00"
    b"\x01\x00\x00\x00\x00\x21\xf9\x04"
    b"\x01\x0a\x00\x01\x00\x2c\x00\x00"
    b"\x00\x00\x01\x00\x01\x00\x00\x02"
    b"\x02\x4c\x01\x00\x3b"
)

User = get_user_model()
NAME = "Test_name"
NAME2 = "Test_name2"
NAME3 = "Test_name3"
EMAIL = "test_email@test.com"
PASSWORD = "pass"


@pytest.fixture(scope="session", autouse=True)
def override_setting_media_root():
    """Переопределяет settings media root."""
    settings.MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@pytest.fixture(scope="session", autouse=True)
def cleanup(request):
    """Очищает тестовую директорию при завершении тестов."""

    def remove_test_dir():
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=False)

    request.addfinalizer(remove_test_dir)


@pytest.fixture
def image():
    return SimpleUploadedFile(
        name="small.gif", content=SMALL_GIF, content_type="image/gif"
    )


@pytest.fixture
def guest_client():
    client = APIClient()
    return client


@pytest.fixture
def moderator_user():
    return User.objects.create_user(
        username=NAME,
        email=EMAIL,
        password=PASSWORD,
        is_moderator=True,
    )


@pytest.fixture
def not_moderator_user():
    return User.objects.create_user(
        username=NAME2,
        email=EMAIL,
        password=PASSWORD,
    )


@pytest.fixture
def user_1():
    return User.objects.create_user(
        username=NAME3,
        email=EMAIL,
        password=PASSWORD,
    )


@pytest.fixture
def not_moderator_client(not_moderator_user):
    client = APIClient()
    client.force_authenticate(user=not_moderator_user)
    return client


@pytest.fixture
def moderator_client(moderator_user):
    client = APIClient()
    client.force_authenticate(user=moderator_user)
    return client


@pytest.fixture
def event(moderator_user):
    return Event.objects.create(
        user=moderator_user,
        title="title",
        type="REGIONAL",
        address="address",
        description="description",
        start_at="3022-12-12T00:00:00Z",
    )


@pytest.fixture
def event_2(moderator_user):
    return Event.objects.create(
        user=moderator_user,
        title="title2",
        type="REGIONAL",
        address="address",
        description="description",
        start_at="2021-12-12T00:00:00Z",
    )


@pytest.fixture
def event_participant(not_moderator_user, event):
    return EventParticipant.objects.create(
        user=not_moderator_user,
        event=event,
    )


@pytest.fixture
def event_participant_2(not_moderator_user, event_2):
    return EventParticipant.objects.create(
        user=not_moderator_user,
        event=event_2,
    )


@pytest.fixture
def review(not_moderator_user, event):
    return Review.objects.create(
        text="text",
        author=not_moderator_user,
        event=event,
        file=SimpleUploadedFile(
            name="small.gif", content=SMALL_GIF, content_type="image/gif"
        ),
        pub_date="2021-12-12T00:00:00Z",
    )


@pytest.fixture
def review_2(not_moderator_user, event_2):
    return Review.objects.create(
        text="text",
        author=not_moderator_user,
        event=event_2,
        file=SimpleUploadedFile(
            name="small.gif", content=SMALL_GIF, content_type="image/gif"
        ),
        pub_date="2021-12-12T00:00:00Z",
    )
