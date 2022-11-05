import shutil
import tempfile
from http import HTTPStatus

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from posts.models import Comment, Group, Post, User

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostsFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание',
        )
        cls.post_group = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
            group=cls.group,
        )
        cls.new_group = Group.objects.create(
            title='Группа для изменения.',
            slug='slug1234',
            description='Изменненое описание',
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_client = Client()
        self.author = Client()
        self.author.force_login(PostsFormTests.user)
        self.authorized_user = User.objects.create_user(username='NotAuthor')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.authorized_user)

    def test_create_post(self):
        """Тест на проверку на создания post
        для не авторизованного пользователя.
        """
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Текст из формы',
        }
        response = self.guest_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertEqual(
            Post.objects.count(),
            posts_count,
            'Изменилось количество постов'
        )
        self.assertRedirects(
            response,
            '/auth/login/?next=/create/'
        )

    def test_create_post_with_group_authorized(self):
        """Тест на проверку на создания post с group
        для авторизованного пользователя.
        """
        posts_count = Post.objects.count()
        group = PostsFormTests.group
        form_data = {
            'text': 'Текст из формы',
            'group': group.id,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTrue(
            Post.objects.filter(
                text=form_data['text'],
                author=self.authorized_user,
                group=group,
            ).exists()
        )

    def test_create_to_add_new_post_authorized(self):
        """Тест на проверку на создания post
        для авторизованного пользователя.
        """
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Текст из формы',
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTrue(
            Post.objects.filter(
                text=form_data['text'],
                author=self.authorized_user,
                group=None,
            ).exists()
        )

    def test_edit_post(self):
        """Тест на проверку на редактирования post
        для не авторизованого пользователя."""
        posts_count = Post.objects.count()
        post = PostsFormTests.post
        form_data = {
            'text': 'Изменный текст',
        }
        response = self.guest_client.post(
            reverse('posts:post_edit', kwargs={'post_id': post.id}),
            data=form_data,
            follow=True
        )
        self.assertTrue(
            Post.objects.filter(
                id=post.id,
                text=post.text,
                author=self.post.author,
                pub_date=post.pub_date,
                group=post.group,
            ).exists(),
            'Изменился пост.'
        )
        self.assertEqual(
            posts_count,
            Post.objects.count(),
            'Появился новый пост.'
        )
        self.assertRedirects(
            response,
            f'/auth/login/?next=/posts/{post.id}/edit/'
        )

    def test_edit_post_authorized_not_author(self):
        """Тест на проверку на редактирования post
        для авторизованого пользователя не автора.
        """
        post = PostsFormTests.post
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Измененный текст',
        }
        response = self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': post.id}),
            data=form_data,
            follow=True
        )
        self.assertTrue(
            Post.objects.filter(
                id=post.id,
                text=post.text,
                author=self.post.author,
                pub_date=post.pub_date,
                group=post.group,
            ).exists(),
            'Изменился пост.'
        )
        self.assertEqual(
            posts_count,
            Post.objects.count(),
            'Появился новый пост.'
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertRedirects(
            response,
            reverse('posts:post_detail', kwargs={'post_id': post.id})
        )

    def test_edit_post_author(self):
        """Тест на проверку на редактирования post для автора."""
        post = PostsFormTests.post
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Измененный текст',
        }
        response = self.author.post(
            reverse('posts:post_edit', kwargs={'post_id': post.id}),
            data=form_data,
            follow=True
        )
        self.assertEqual(
            posts_count,
            Post.objects.count(),
            'Не совпадает количестов постов после редактирования.'
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTrue(
            Post.objects.filter(
                id=post.id,
                text=form_data['text'],
                author=post.author,
                group=None,
            ).exists(),
            'Пост не изменился.'
        )
        self.assertRedirects(
            response,
            reverse('posts:post_detail', kwargs={'post_id': post.id})
        )

    def test_edit_post_with_group_author(self):
        """Тест на проверку на редактирования post c группой для автора."""
        post_group = PostsFormTests.post
        posts_count = Post.objects.count()
        group = PostsFormTests.new_group
        form_data = {
            'text': 'Измененный текст',
            'group': group.id,
        }
        response = self.author.post(
            reverse('posts:post_edit', kwargs={'post_id': post_group.id}),
            data=form_data,
            follow=True
        )
        self.assertEqual(
            posts_count,
            Post.objects.count(),
            'Не совпадает количестов постов после редактирования.'
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTrue(
            Post.objects.filter(
                id=post_group.id,
                text=form_data['text'],
                author=post_group.author,
                group=group,
            ).exists(),
            'Пост с группой не изменился.'
        )
        self.assertRedirects(
            response,
            reverse('posts:post_detail', kwargs={'post_id': post_group.id})
        )

    def test_created_comment_only_authorized(self):
        """Тест на проверку создания комментариев для авторизованного."""
        post = PostsFormTests.post
        comment_count = post.comments.count()
        form_data = {
            'text': 'Коммент',
        }
        response = self.authorized_client.post(
            reverse('posts:add_comment', kwargs={'post_id': post.id}),
            data=form_data,
            follow=True
        )
        self.assertTrue(
            Comment.objects.filter(
                post=post,
                text=form_data['text'],
                author=self.authorized_user,
            ).exists(),
        )
        self.assertEqual(
            post.comments.count(),
            comment_count + 1,
            'Не появился новый коммент.'
        )
        self.assertRedirects(
            response,
            reverse('posts:post_detail', kwargs={'post_id': post.id})
        )

    def test_create_post_with_image_authorized(self):
        """Тест на проверку на создания post с картинкой
        для авторизованного пользователя.
        """
        posts_count = Post.objects.count()
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x0B'
        )
        uploaded = SimpleUploadedFile(
            name='image.gif',
            content=small_gif,
            content_type='image/gif'
        )
        form_data = {
            'text': 'Текст из формы',
            'image': uploaded,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTrue(
            Post.objects.filter(
                text=form_data['text'],
                author=self.authorized_user,
                image='posts/image.gif'
            ).exists()
        )
