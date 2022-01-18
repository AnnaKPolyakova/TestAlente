import pytest
from django.urls import reverse

MY_EVENTS_URL = reverse("my_events")

pytestmark = pytest.mark.django_db


class TestMyEventAPI:
    @pytest.mark.parametrize(
        "user_client, code",
        [
            (pytest.lazy_fixture("moderator_client"), 403),
            (pytest.lazy_fixture("not_moderator_client"), 200),
            (pytest.lazy_fixture("guest_client"), 403),
        ],
    )
    def test_get_my_events_url(self, user_client, code):
        """
        Только зарегистрированный не модератор может запросить список
        мероприятий, на которые он подписан
        """
        url = MY_EVENTS_URL
        response = user_client.get(url)
        assert response.status_code == code, (
            f"Проверьте, что при GET запросе {url} " f"возвращается статус {code}"
        )
