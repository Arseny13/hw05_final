from http import HTTPStatus

from django.test import Client, TestCase

from posts.models import Group, Post, User


class PostsURLTests(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='HasNoName')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.author = Client()
        self.author.force_login(PostsURLTests.user)

    def test_urls_exists(self):
        """Проверка статусов URL для неавторизованных пользователей."""
        post = PostsURLTests.post
        group = PostsURLTests.group
        urls = {
            '/': HTTPStatus.OK,
            f'/group/{group.slug}/': HTTPStatus.OK,
            f'/posts/{post.id}/': HTTPStatus.OK,
            f'/profile/{post.author.username}/': HTTPStatus.OK,
            '/follow/': HTTPStatus.FOUND,
            'unexising_page': HTTPStatus.NOT_FOUND,
        }
        for address, code in urls.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertEqual(response.status_code, code)

    def test_urls_status_exists_authorized(self):
        """Проверка статусов URL
        для авторизованного пользователя.
        """
        post = PostsURLTests.post
        group = PostsURLTests.group
        urls = {
            '/': HTTPStatus.OK,
            f'/group/{group.slug}/': HTTPStatus.OK,
            f'/posts/{post.id}/': HTTPStatus.OK,
            f'/profile/{post.author.username}/': HTTPStatus.OK,
            '/create/': HTTPStatus.OK,
            '/follow/': HTTPStatus.OK,
            '/unexising_page': HTTPStatus.NOT_FOUND,
        }
        for address, code in urls.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertEqual(response.status_code, code)

    def test_post_edit_url_redirect_post_detail(self):
        """Страница по адресу /post/edit/ перенаправит
        не авторизованного пользователя на страницу входа.
        """
        post = PostsURLTests.post
        response = self.guest_client.get(
            f'/posts/{post.id}/edit/',
            follow=True
        )
        self.assertRedirects(
            response,
            f'/auth/login/?next=/posts/{post.id}/edit/'
        )

    def test_post_edit_url_redirect_not_author_post_detail(self):
        """Страница по адресу /post/edit/ перенаправит не автора поста
        на страницу инфорции о посте.
        """
        post = PostsURLTests.post
        response = self.authorized_client.get(
            f'/posts/{post.id}/edit/',
            follow=True
        )
        self.assertRedirects(
            response, f'/posts/{post.id}/'
        )

    def test_urls_exists_authorized(self):
        """URL-адрес использует соответствующий шаблон"""
        post = PostsURLTests.post
        group = PostsURLTests.group
        templates_url_names = {
            '/': 'posts/index.html',
            f'/group/{group.slug}/': 'posts/group_list.html',
            f'/posts/{post.id}/': 'posts/post_detail.html',
            f'/profile/{post.author.username}/': 'posts/profile.html',
            '/create/': 'posts/create_post.html',
            '/follow/': 'posts/follow.html',
        }
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)
