from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

User = get_user_model()


class UsersCRUDTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="johndoe",
            password="pass1234",
            first_name="John",
            last_name="Doe",
        )

    def test_user_registration(self):
        response = self.client.post(
            reverse("user_create"),
            {
                "username": "newuser",
                "password1": "StrongPass123",
                "password2": "StrongPass123",
                "first_name": "Alice",
                "last_name": "Smith",
            },
        )

        self.assertRedirects(response, reverse("login"))
        self.assertTrue(User.objects.filter(username="newuser").exists())

    def test_user_update_self(self):
        self.client.login(username="johndoe", password="pass1234")
        update_url = reverse("user_update", kwargs={"pk": self.user.pk})

        response = self.client.post(
            update_url,
            {
                "username": "johndoe",
                "first_name": "Updated",
                "last_name": "User",
                "current_username": "johndoe",
            },
        )

        self.assertRedirects(response, reverse("user_list"))
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, "Updated")
        self.assertEqual(self.user.last_name, "User")

    def test_user_delete_self(self):
        self.client.login(username="johndoe", password="pass1234")
        delete_url = reverse("user_delete", kwargs={"pk": self.user.pk})

        response = self.client.post(delete_url)

        self.assertRedirects(response, reverse("user_list"))
        self.assertFalse(User.objects.filter(username="johndoe").exists())

    def test_update_other_user_forbidden(self):
        other_user = User.objects.create_user(
            username="other", password="pass4321"
        )
        self.client.login(username="johndoe", password="pass1234")

        response = self.client.get(
            reverse("user_update", kwargs={"pk": other_user.pk})
        )
        self.assertEqual(response.status_code, 403)

    def test_delete_other_user_forbidden(self):
        other_user = User.objects.create_user(
            username="other", password="pass4321"
        )
        self.client.login(username="johndoe", password="pass1234")

        response = self.client.post(
            reverse("user_delete", kwargs={"pk": other_user.pk})
        )
        self.assertEqual(response.status_code, 403)
