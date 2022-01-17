import pytest
from django.urls import reverse

pytestmark = pytest.mark.django_db

EVENT_REVIEWS_URL = "reviews-list"


class TestReviewsAPI:

    @pytest.mark.parametrize(
        "user_client, code",
        [
            (pytest.lazy_fixture("moderator_client"), 403),
            (pytest.lazy_fixture("not_moderator_client"), 201),
            (pytest.lazy_fixture("guest_client"), 403),
        ],
    )
    def test_post_event_reviews_url(
            self, user_client, code, event2, event_participant, image
    ):
        """
        Только не модератор может оставить отзыв на прошедшее событие,
        на которое он был зарегистрирован
        """
        url = reverse(EVENT_REVIEWS_URL, args=[event2.id])
        data = {
            "text": "text",
            "file": image,
        }
        response = user_client.post(url, data=data, format="multipart")
        assert response.status_code == code, (
            f"Проверьте, что при POST запросе {url} "
            f"возвращается статус {code}"
        )

    def test_post_event_reviews_without_registration_url(
            self, not_moderator_client, event, image
    ):
        """
        Не модератор не может оставить отзыв на событие,
        на которое он не был зарегистрирован
        """
        url = reverse(EVENT_REVIEWS_URL, args=[event.id])
        data = {
            "text": "text",
            "file": image,
        }
        response = not_moderator_client.post(url, data=data, format="multipart")
        assert response.status_code == 400, (
            f"Проверьте, что при POST запросе {url} "
            f"возвращается статус 400"
        )