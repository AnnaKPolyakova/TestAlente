import pytest
from django.urls import reverse

USER_LIST_URL = reverse("user-list")
USER_DETAIL_URL = "user-detail"

pytestmark = pytest.mark.django_db


class TestUserAPI:
    """
    Любой пользователь может создать пользователя
    """
    def test_create_user_url(self, guest_client):
        url = USER_LIST_URL
        data = {
            "username": "Testy",
            "email": "test@test6.ru",
            "password": "testtest"
        }
        response = guest_client.post(url, data=data)
        assert response.status_code == 201, (
            f"Проверьте, что при POST запросе {url} "
            f"возвращается статус 201"
        )

    @pytest.mark.parametrize(
        "user_client, code",
        [
            (pytest.lazy_fixture("moderator_client"), 200),
            (pytest.lazy_fixture("not_moderator_client"), 403),
        ],
    )
    def test_get_user_url(self, user_client, code):
        """
        Информацию обо всех пользователях может видеть только модератор
        """
        url = USER_LIST_URL
        response = user_client.get(url)
        assert response.status_code == code, (
            f"Проверьте, что при GET запросе {url} возвращается статус {code}"
        )
        assert len(response.data) == 1, (
            f"Проверьте, что при GET запросе {url} возвращается статус {code}"
        )

    @pytest.mark.parametrize(
        "user_client, code",
        [
            (pytest.lazy_fixture("moderator_client"), 200),
            (pytest.lazy_fixture("not_moderator_client"), 403),
        ],
    )
    def test_patch_user_url(self, user_client, code, user_1):
        """
        Информацию обо всех пользователях может изменять только модератор
        """
        url = reverse(USER_DETAIL_URL, args=[user_1.id])
        data = {
            "moderator": True
        }
        response = user_client.patch(url, data=data)
        assert response.status_code == code, (
            f"Проверьте, что при PATCH запросе {url} "
            f"возвращается " f"статус {code}"
        )

    @pytest.mark.parametrize(
        "data, code",
        [
            ({"email": "test2@test.ru"}, 200),
            ({"moderator": True}, 403),
        ],
    )
    def test_patch_user_url(
            self, data, code, not_moderator_client, not_moderator_user
    ):
        """
        Не модератор может менять любые свои данные, но не может сделать себя
        модератором
        """
        url = reverse(USER_DETAIL_URL, args=[not_moderator_user.id])
        response = not_moderator_client.patch(url, data=data)
        assert response.status_code == code, (
            f"Проверьте, что при PATCH запросе {url} "
            f"возвращается " f"статус {code}"
        )

    @pytest.mark.parametrize(
        "user_client, code",
        [
            (pytest.lazy_fixture("moderator_client"), 204),
            (pytest.lazy_fixture("not_moderator_client"), 403),
        ],
    )
    def test_delete_user_url(self, user_client, code, user_1):
        """
        Только модератор может удалить любого пользователя
        """
        url = reverse(USER_DETAIL_URL, args=[user_1.id])
        response = user_client.delete(url)
        assert response.status_code == code, (
            f"Проверьте, что при DELETE запросе {url} "
            f"возвращается " f"статус {code}"
        )
