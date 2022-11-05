from http import HTTPStatus

from django.test import Client, TestCase


class UsersViewsTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_404_exists(self):
        """URL-адрес 404 использует соответствующий шаблон"""
        response = self.guest_client.get('/nonexist-page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertTemplateUsed(response, 'core/404.html')
