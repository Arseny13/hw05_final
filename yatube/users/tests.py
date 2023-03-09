from django import forms
from django.test import Client, TestCase
from django.urls import reverse
from posts.models import User


class UsersViewsTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_signup_exists(self):
        """URL-адрес использует соответствующий шаблон"""
        response = self.guest_client.get(reverse('users:signup'))
        self.assertTemplateUsed(response, 'users/signup.html')

    def test_signup_correct_context(self):
        """Шаблон signup сформирован с правильным контекстом."""
        response = self.guest_client.get(reverse('users:signup'))
        form_fields = {
            'first_name': forms.fields.CharField,
            'last_name': forms.fields.CharField,
            'username': forms.fields.CharField,
            'email': forms.fields.EmailField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(
                    form_field,
                    expected,
                    'Не правильный тип у полей формы.'
                )

    def test_signup_to_add_new_user(self):
        """Тест на создание нового user."""
        users_count = User.objects.count()
        url = reverse('users:signup')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        form_data = {
            'first_name': 'FIRSTNAME',
            'last_name': 'LASTNAME',
            'username': 'testuser',
            'email': 'test_user@gmail.com',
            'password1': 'password123qwer',
            'password2': 'password123qwer',
        }
        response = self.guest_client.post(
            url,
            data=form_data,
            follow=True
        )
        self.assertEqual(User.objects.count(), users_count + 1)
        self.assertTrue(
            User.objects.filter(
                username='testuser'
            )
        )
        self.assertRedirects(
            response,
            reverse('users:login')
        )
