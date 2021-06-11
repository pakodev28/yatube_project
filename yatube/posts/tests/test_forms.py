import shutil
import tempfile

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post

User = get_user_model()


class FormPostTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        settings.MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Это тестовая группа'
        )
        cls.user = User.objects.create_user(username='mr.test')
        cls.post = Post.objects.create(text='Тестовый пост!', author=cls.user)

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(FormPostTests.user)

    def tearDown(self):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)

    def test_create_new_post(self):
        post_count = Post.objects.count()
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        form_data = {
            'text': 'Тестовый пост',
            'author': FormPostTests.user,
            'image': uploaded,
        }

        response = self.authorized_client.post(
            reverse('new_post'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse('index'))
        self.assertEqual(Post.objects.count(), post_count + 1)
        self.assertTrue(
            Post.objects.filter(
                text='Тестовый пост',
                author=FormPostTests.user,).exists())

    def test_edit_post(self):
        post = FormPostTests.post
        form_data = {'text': 'Тестовый пост измененный'}
        response = self.authorized_client.post(
            reverse('post_edit',
                    kwargs={'username': self.user.username,
                            'post_id': post.id}),
            data=form_data,
            follow=True)
        self.assertRedirects(response, reverse(
            'post',
            kwargs={'username': self.user.username,
                    'post_id': post.id}))
        self.assertEqual(Post.objects.count(), 1)
        self.assertTrue(Post.objects.filter(text=form_data['text']).exists())

    def test_unauthorized_user_create_new_post(self):
        post_count = Post.objects.count()
        response = self.guest_client.get(reverse('new_post'))
        self.assertEqual(Post.objects.count(), post_count)
        self.assertRedirects(
            response,
            reverse('login') + '?next=' + reverse('new_post')
        )
