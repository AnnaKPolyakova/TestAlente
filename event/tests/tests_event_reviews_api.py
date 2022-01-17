import pytest
from django.urls import reverse

from event.models import Review

pytestmark = pytest.mark.django_db

EVENT_REVIEWS_LIST_URL = "reviews-list"
EVENT_REVIEWS_DETAIL_URL = "reviews-detail"


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
            self, user_client, code, event_2, event_participant_2, image
    ):
        """
        Только не модератор может оставить отзыв на прошедшее событие,
        на которое он был зарегистрирован
        """
        url = reverse(EVENT_REVIEWS_LIST_URL, args=[event_2.id])
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
        url = reverse(EVENT_REVIEWS_LIST_URL, args=[event.id])
        data = {
            "text": "text",
            "file": image,
        }
        response = not_moderator_client.post(url, data=data, format="multipart")
        assert response.status_code == 400, (
            f"Проверьте, что при POST запросе {url} "
            f"возвращается статус 400"
        )

    def test_post_reviews_for_pending_event(
            self, not_moderator_client, event, image, event_participant_2
    ):
        """
        Не модератор не может оставить отзыв на событие,
        которое еще не наступило
        """
        url = reverse(EVENT_REVIEWS_LIST_URL, args=[event.id])
        data = {
            "text": "text",
            "file": image,
        }
        response = not_moderator_client.post(url, data=data, format="multipart")
        assert response.status_code == 400, (
            f"Проверьте, что при POST запросе {url} "
            f"возвращается статус 400"
        )

    def test_post_more_than_one_reviews_for_one_event(
            self, not_moderator_client, event_2, image,
            event_participant_2, review_2
    ):
        """
        Не модератор не может оставить больше одного отзыва
        """
        url = reverse(EVENT_REVIEWS_LIST_URL, args=[event_2.id])
        data = {
            "text": "text",
            "file": image,
        }
        response = not_moderator_client.post(url, data=data, format="multipart")
        assert response.status_code == 400, (
            f"Проверьте, что при POST запросе {url} "
            f"возвращается статус 400"
        )

    @pytest.mark.parametrize(
        "user_client, code",
        [
            (pytest.lazy_fixture("moderator_client"), 200),
            (pytest.lazy_fixture("not_moderator_client"), 200),
            (pytest.lazy_fixture("guest_client"), 200),
        ],
    )
    def test_get_event_reviews_url(
            self, user_client, code, event_2, review_2
    ):
        """
        Любой может увидеть отзывы
        """
        urls = [
            reverse(EVENT_REVIEWS_LIST_URL, args=[event_2.id]),
            reverse(EVENT_REVIEWS_DETAIL_URL, args=[event_2.id, review_2.id]),
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
            (pytest.lazy_fixture("not_moderator_client"), 200),
            (pytest.lazy_fixture("guest_client"), 200),
        ],
    )
    def test_get_event_reviews_count_objects_url(
            self, user_client, code, event_2, review_2
    ):
        """
        Запрос возвращает верное кол-во объектов
        """
        url = reverse(EVENT_REVIEWS_LIST_URL, args=[event_2.id])
        response = user_client.get(url)
        assert response.data["count"] == Review.objects.all().count(), (
                f"Проверьте, что при GET запросе {url} "
                f"возвращается данные объектов"
            )

    @pytest.mark.parametrize(
        "user_client, code",
        [
            (pytest.lazy_fixture("moderator_client"), 200),
            (pytest.lazy_fixture("not_moderator_client"), 200),
            (pytest.lazy_fixture("guest_client"), 200),
        ],
    )
    def test_get_event_reviews_detail_count_objects_url(
            self, user_client, code, event_2, review_2
    ):
        """
        Запрос возвращает верное кол-во объектов
        """
        url = reverse(EVENT_REVIEWS_DETAIL_URL, args=[event_2.id, review_2.id])
        response = user_client.get(url)
        assert len(response.data) == 6, (
                f"Проверьте, что при GET запросе {url} "
                f"возвращается данные объектов"
            )

    @pytest.mark.parametrize(
        "user_client, code",
        [
            (pytest.lazy_fixture("moderator_client"), 403),
            (pytest.lazy_fixture("not_moderator_client"), 200),
            (pytest.lazy_fixture("guest_client"), 403),
        ],
    )
    def test_patch_event_reviews_url(
            self, user_client, code, event_2, review_2, image
    ):
        """
        Пользователь может изменить только свой отзыв
        """
        url = reverse(EVENT_REVIEWS_DETAIL_URL, args=[event_2.id, review_2.id])
        data = {
            "text": "text",
            "file": image,
        }
        response = user_client.patch(url, data=data, format="multipart")
        assert response.status_code == code, (
            f"Проверьте, что при PATCH запросе {url} "
            f"возвращается статус {code}"
        )

    @pytest.mark.parametrize(
        "user_client, code",
        [
            (pytest.lazy_fixture("moderator_client"), 403),
            (pytest.lazy_fixture("not_moderator_client"), 204),
            (pytest.lazy_fixture("guest_client"), 403),
        ],
    )
    def test_delete_event_reviews_url(
            self, user_client, code, event_2, review_2, image
    ):
        """
        Пользователь может удалить только свой отзыв
        """
        url = reverse(EVENT_REVIEWS_DETAIL_URL, args=[event_2.id, review_2.id])
        data = {
            "text": "text",
            "file": image,
        }
        response = user_client.delete(url, data=data, format="multipart")
        assert response.status_code == code, (
            f"Проверьте, что при PATCH запросе {url} "
            f"возвращается статус {code}"
        )

