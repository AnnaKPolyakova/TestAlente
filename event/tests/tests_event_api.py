import pytest
from django.urls import reverse

EVENT_LIST_URL = reverse("event-list")
EVENT_DETAIL_URL = "event-detail"

pytestmark = pytest.mark.django_db


class TestEventAPI:

    @pytest.mark.parametrize(
        "user_client, code",
        [
            (pytest.lazy_fixture("moderator_client"), 201),
            (pytest.lazy_fixture("not_moderator_client"), 403),
            (pytest.lazy_fixture("guest_client"), 403),
        ],
    )
    def test_create_event_url(self, user_client, code):
        """
        Только модератор может создать событие
        """
        url = EVENT_LIST_URL
        data = {
            "title": "title",
            "type": "REGIONAL",
            "address": "address",
            "description": "description",
            "start_at": "2022-12-12T00:00:00Z",
        }
        response = user_client.post(url, data=data)
        assert response.status_code == code, (
            f"Проверьте, что при POST запросе {url} "
            f"возвращается статус {code}"
        )

    @pytest.mark.parametrize(
        "user_client, code",
        [
            (pytest.lazy_fixture("moderator_client"), 200),
            (pytest.lazy_fixture("not_moderator_client"), 200),
            (pytest.lazy_fixture("guest_client"), 200),
        ],
    )
    def test_get_event_url(self, user_client, code, event):
        """
        Любой может посмотреть все события
        """
        urls = [
            EVENT_LIST_URL,
            reverse(EVENT_DETAIL_URL, args=[event.id])
        ]
        for url in urls:
            response = user_client.get(url)
            assert response.status_code == code, (
                f"Проверьте, что при GET запросе {url} "
                f"возвращается статус {code}"
            )

    @pytest.mark.parametrize(
        "user_client, code",
        [
            (pytest.lazy_fixture("moderator_client"), 200),
            (pytest.lazy_fixture("not_moderator_client"), 403),
            (pytest.lazy_fixture("guest_client"), 403),
        ],
    )
    def test_patch_event_url(self, user_client, code, event):
        """
        Только модератор может изменить событие
        """
        url = reverse(EVENT_DETAIL_URL, args=[event.id])
        data = {
            "address": "address2",
        }
        response = user_client.patch(url, data=data)
        assert response.status_code == code, (
            f"Проверьте, что при PATCH запросе {url} "
            f"возвращается статус {code}"
        )

    @pytest.mark.parametrize(
        "user_client, code",
        [
            (pytest.lazy_fixture("moderator_client"), 204),
            (pytest.lazy_fixture("not_moderator_client"), 403),
            (pytest.lazy_fixture("guest_client"), 403),
        ],
    )
    def test_delete_event_url(self, user_client, code, event):
        """
        Только модератор может удалить событие
        """
        url = reverse(EVENT_DETAIL_URL, args=[event.id])
        data = {
            "address": "address2",
        }
        response = user_client.delete(url, data=data)
        assert response.status_code == code, (
            f"Проверьте, что при DELETE запросе {url} "
            f"возвращается статус {code}"
        )
