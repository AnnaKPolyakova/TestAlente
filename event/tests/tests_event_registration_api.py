import pytest
from django.urls import reverse

EVENT_REGISTRATION_URL = "event_registration"

pytestmark = pytest.mark.django_db


class TestEventAPI:

    @pytest.mark.parametrize(
        "user_client, code",
        [
            (pytest.lazy_fixture("moderator_client"), 403),
            (pytest.lazy_fixture("not_moderator_client"), 200),
            (pytest.lazy_fixture("guest_client"), 403),
        ],
    )
    def test_event_registration_url(self, user_client, code, event):
        """
        Только не модератор может подать заявку на регистрацию
        """
        url = reverse(EVENT_REGISTRATION_URL, args=[event.id])
        response = user_client.post(url)
        assert response.status_code == code, (
            f"Проверьте, что при POST запросе {url} "
            f"возвращается статус {code}"
        )
