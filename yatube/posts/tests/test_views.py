import shutil
import tempfile

from django import forms
from django.conf import settings
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from posts.models import Follow, Group, Post, User

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostsPagesTests(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        """Создание фикстур для тестов."""
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.another_user = User.objects.create_user(username='another')
        Follow.objects.create(
            user=cls.user,
            author=cls.another_user,
        )
        cls.post_cache = Post.objects.create(
            author=cls.user,
            text='Тестовый пост для кеша',
        )
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание',
        )
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='test.gif',
            content=small_gif,
            content_type='image/gif'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
            group=cls.group,
            image=uploaded,
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        """Создание клиентов."""
        self.author_client = Client()
        self.author_client.force_login(PostsPagesTests.user)
        self.user = User.objects.create_user(username='StasBasov')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        post = PostsPagesTests.post
        group = PostsPagesTests.group
        templates_pages_names = {
            'posts/index.html': reverse('posts:index'),
            'posts/create_post.html': reverse('posts:post_create'),
            'posts/group_list.html': reverse(
                'posts:group_list',
                kwargs={'slug': group.slug}
            ),
            'posts/post_detail.html': (
                reverse('posts:post_detail', kwargs={'post_id': post.id})
            ),
        }
        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(
                    response,
                    template,
                    'Url не соответсвует html.'
                )

    def test_create_post_show_correct_context(self):
        """Шаблон create_post сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
            'image': forms.fields.ImageField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(
                    form_field,
                    expected,
                    'Не правильный тип у полей формы.'
                )
        self.assertFalse(
            response.context.get('is_edit'),
            'Передается is_edit'
        )

    def test_edit_post_show_correct_context(self):
        """Шаблон edit_post сформирован с правильным контекстом."""
        post = PostsPagesTests.post
        response = self.author_client.get(
            reverse('posts:post_edit', kwargs={'post_id': post.id})
        )
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
            'image': forms.fields.ImageField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(
                    form_field,
                    expected,
                    'Не правильный тип у полей формы'
                )
        self.assertTrue(
            response.context.get('is_edit'),
            'Не передается is_edit'
        )
        self.assertEqual(
            response.context.get('id'),
            post.id,
            'Передан другой id поста.'
        )

    def test_post_detail_show_correct_context(self):
        """Шаблон post_detail с правильным контекстом."""
        post = PostsPagesTests.post
        response = self.authorized_client.get(
            reverse('posts:post_detail', kwargs={'post_id': post.id})
        )
        self.assertEqual(
            response.context.get('post'),
            post,
            'Не правильный пост.'
        )
        self.assertEqual(
            response.context.get('post').group,
            post.group,
            'Не правильная группа.'
        )
        self.assertEqual(
            response.context.get('post').image,
            post.image,
            'Не та картинка.'
        )
        self.assertEqual(
            response.context.get('post').author,
            post.author,
            'Другой автор.'
        )

    def test_urls_show_correct_image(self):
        """Пост с картинкой показавает на главной странице,
        на странице профайла, на странице группы
        правильный контекст картинки.
        """
        urls = [
            reverse('posts:index'),
            reverse(
                'posts:group_list',
                kwargs={'slug': self.group.slug}
            ),
            reverse(
                'posts:profile',
                kwargs={'username': self.post.author.username}
            ),
        ]
        for url in urls:
            with self.subTest(value=url):
                response = self.authorized_client.get(url)
                self.assertEqual(
                    response.context['page_obj'][0].image,
                    self.post.image,
                    'Не та картинка.'
                )

    def test_post_profile_show_correct_image(self):
        """Пост с картинкой показавает на странице поста
        правильный контекст картинки."""
        response = self.authorized_client.get(
            reverse(
                'posts:post_detail',
                kwargs={'post_id': self.post.id}
            )
        )
        self.assertEqual(
            response.context.get('post').image,
            self.post.image,
            'Не та картинка.'
        )

    def test_new_post_show_urls(self):
        """Пост с группой показан на главной странице,
        на странице группы и автора поста.
        """
        urls = [
            reverse('posts:index'),
            reverse(
                'posts:group_list',
                kwargs={'slug': self.group.slug}
            ),
            reverse(
                'posts:profile',
                kwargs={'username': self.post.author.username}
            )
        ]
        for url in urls:
            with self.subTest(value=url):
                response = self.authorized_client.get(url)
                first_object = response.context.get('page_obj').object_list[0]
                self.assertEqual(first_object.text, 'Тестовый пост')
                self.assertEqual(
                    first_object.group.slug,
                    'test_slug',
                    'Пост попал в другую группу.'
                )

    def test_profile_show_correct_context(self):
        """Старница профиль пользователя имеет правильный контекст author."""
        response = self.authorized_client.get(
            reverse(
                'posts:profile',
                kwargs={'username': self.post.author.username}
            )
        )
        self.assertEqual(
            response.context.get('author'),
            self.post.author,
            'Контекст автор не совпадает с создателем поста.'
        )

    def test_group_list_show_correct_context(self):
        """Старница группы имеет правильный контекст group."""
        response = self.authorized_client.get(
            reverse(
                'posts:group_list',
                kwargs={'slug': self.group.slug}
            )
        )
        self.assertEqual(
            response.context.get('group'),
            self.group,
            'Контекст группа не совпадает с группой.'
        )

    def test_post_detail_show_comment(self):
        """Страница поста показывает комментарий."""
        post = PostsPagesTests.post
        form_data = {
            'text': 'Коммент',
        }
        response = self.authorized_client.post(
            reverse('posts:add_comment', kwargs={'post_id': post.id}),
            data=form_data,
            follow=True
        )
        response = self.authorized_client.get(
            reverse('posts:post_detail', kwargs={'post_id': post.id})
        )
        self.assertEqual(
            response.context.get('comments')[0].text,
            form_data['text'],
            'Контекст комментария не совпадает с текстом отрпавленного.'
        )
        self.assertEqual(
            response.context.get('comments')[0].post,
            post,
            'Комментарий относится не к тому посту.'
        )

    def test_checked_cache(self):
        """Проверка кеша на главной странице"""
        url = reverse('posts:index')
        response_old = self.authorized_client.get(url)
        self.post_cache.delete()
        response = self.authorized_client.get(url)
        self.assertEqual(response.content, response_old.content)
        cache.clear()
        response_new = self.authorized_client.get(url)
        self.assertNotEqual(response.content, response_new.content)

    def test_profile_follow_work(self):
        """Тест на создания новой подписки у авторизованного пользователя."""
        follow_count = Follow.objects.filter(user=self.user).count()
        self.authorized_client.get(
            reverse(
                'posts:profile_follow',
                kwargs={'username': self.post.author.username}
            )
        )
        self.assertEqual(
            Follow.objects.filter(user=self.user).count(),
            follow_count + 1,
        )
        self.assertTrue(
            Follow.objects.filter(
                user=self.user,
                author=self.post.author,
            ).exists()
        )

    def test_profile_unfollow_work(self):
        """Тест на отмену подписки у авторизованного пользователя."""
        follow_count = Follow.objects.filter(user=self.post.author).count()
        self.author_client.get(
            reverse(
                'posts:profile_unfollow',
                kwargs={'username': self.another_user.username}
            )
        )
        self.assertEqual(
            Follow.objects.filter(user=self.post.author).count(),
            follow_count - 1,
        )
        self.assertFalse(
            Follow.objects.filter(
                user=self.post.author,
                author=self.another_user,
            ).exists()
        )

    def test_new_post_show_follow_user(self):
        """Проверка новый пост появляется у подписчика
        и не появляется у не подписчика.
        (автор на себя не подписан)"""
        self.authorized_client.get(
            reverse(
                'posts:profile_follow',
                kwargs={'username': self.post.author.username}
            )
        )
        Post.objects.create(
            author=self.post.author,
            text='Новый пост для подписчика.'
        )
        response = self.authorized_client.get(
            reverse(
                'posts:follow_index',
            )
        )
        self.assertEqual(
            response.context.get('page_obj').object_list[0].text,
            'Новый пост для подписчика.',
            'Текст не совпадает .'
        )
        response = self.author_client.get(
            reverse(
                'posts:follow_index',
            )
        )
        self.assertEqual(
            len(response.context.get('page_obj').object_list),
            0,
        )


class PaginatorViewsTest(TestCase):
    COUNT_POST = 15
    COUNT_POST_PAGE = 10

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание',
        )
        cls.user = User.objects.create_user(username='auth')
        objs = [
            Post(
                text='Тестовый пост %s' % i,
                group=cls.group,
                author=cls.user,
            )
            for i in range(cls.COUNT_POST)
        ]
        Post.objects.bulk_create(objs=objs)

    def setUp(self):
        self.user = User.objects.create_user(username='test_user')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_first_page_contains_ten_records(self):
        """Пагинатор показывает 10 постов на первой странице."""
        responses = [
            self.authorized_client.get(reverse('posts:index')),
            self.authorized_client.get(
                reverse('posts:group_list',
                        kwargs={'slug': 'test_slug'})
            ),
            self.authorized_client.get(
                reverse('posts:profile', kwargs={'username': 'auth'})
            ),
        ]
        for response in responses:
            with self.subTest(value=response):
                self.assertEqual(
                    len(response.context.get('page_obj').object_list),
                    self.COUNT_POST_PAGE
                )

    def test_second_page_contains_five_records(self):
        """Пагинатор показывает 5 постов на второй странице."""
        responses = [
            self.authorized_client.get(f"{reverse('posts:index')}?page=2"),
            self.authorized_client.get(
                f"{reverse('posts:group_list', kwargs={'slug': 'test_slug'})}"
                f"?page=2"
            ),
            self.authorized_client.get(
                f"{reverse('posts:profile', kwargs={'username': 'auth'})}"
                f"?page=2"
            ),
        ]
        for response in responses:
            with self.subTest(value=response):
                self.assertEqual(
                    len(response.context.get('page_obj').object_list),
                    self.COUNT_POST - self.COUNT_POST_PAGE,
                    'Количество записей не совпадает.'
                )
