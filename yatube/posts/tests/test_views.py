import shutil
import tempfile

from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post

User = get_user_model()


class ViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        settings.MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

        cls.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=cls.small_gif,
            content_type='image/gif'
        )
        cls.user = User.objects.create_user(username='mr.test')
        cls.user_2 = User.objects.create_user(username='follower user')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Это тестовая группа'
        )
        cls.group_2 = Group.objects.create(title='Тестовая группа два',
                                           slug='test-slug-2')
        cls.post = Post.objects.create(text='Тестовый пост',
                                       author=cls.user,
                                       group=cls.group,
                                       image=cls.uploaded)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(ViewsTests.user)
        self.auth_client = Client()
        self.auth_client.force_login(ViewsTests.user_2)
        self.guest_client = Client()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)

    def test_pages_use_correct_template(self):
        templates_pages_names = {
            'index.html': reverse('index'),
            'group.html': reverse(
                'slug',
                kwargs={'slug': ViewsTests.group.slug}),
            'new_post.html': reverse('new_post'),
        }
        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_page_use_correct_context(self):
        response = self.authorized_client.get(reverse('index'))
        received_post = response.context.get('page')[0]
        expected = ViewsTests.post
        self.assertEqual(expected, received_post)
        self.assertEqual(received_post.image, 'posts/small.gif')

    def test_group_page_use_correct_context(self):
        response = self.authorized_client.get(
            reverse('slug',
                    kwargs={'slug': ViewsTests.group.slug}))
        first_object = response.context['group']
        group_title_0 = first_object.title
        group_slug_0 = first_object.slug
        group_desc_0 = first_object.description
        self.assertEqual(group_title_0, 'Тестовая группа')
        self.assertEqual(group_slug_0, 'test-slug')
        self.assertEqual(group_desc_0, 'Это тестовая группа')
        self.assertEqual(response.context.get('page')[0].image,
                         'posts/small.gif')

    def test_new_post_use_correct_context(self):
        response = self.authorized_client.get(reverse('new_post'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_post_edit_use_correct_context(self):
        response = self.authorized_client.get(
            reverse('post_edit',
                    kwargs={'username': self.user.username,
                            'post_id': self.post.id}),
        )
        form_fields = {
            'text': forms.fields.CharField,
        }

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields[value]
                self.assertIsInstance(form_field, expected)

    def test_profile_use_correct_context(self):
        response = self.authorized_client.get(
            reverse('profile',
                    kwargs={'username': self.user.username})
        )
        self.assertEqual(response.context['author'], self.user)
        self.assertEqual(response.context.get('page')[0], self.post)
        self.assertEqual(response.context.get('page')[0].image,
                         'posts/small.gif')

    def test_post_use_correct_context(self):
        response = self.authorized_client.get(
            reverse('post',
                    kwargs={'username': self.user.username,
                            'post_id': self.post.id})
        )

        post_context = {'post_count': self.user.user_posts.all().count(),
                        'author': self.post.author,
                        'post': self.post}

        for value, expected in post_context.items():
            with self.subTest(value=value):
                context = response.context[value]
                self.assertEqual(context, expected)

    def test_new_post_added_on_page(self):
        pages = (
            reverse('index'),
            reverse('slug', kwargs={'slug': ViewsTests.group.slug}))
        for page in pages:
            with self.subTest(value=page):
                response = self.authorized_client.get(page)
                self.assertContains(response, ViewsTests.post.text)

    def test_new_post_not_added_on_page(self):
        response = self.authorized_client.get(
            reverse('slug', kwargs={'slug': ViewsTests.group_2.slug}))
        self.assertNotContains(response, ViewsTests.post.text)

    def test_index_page_caching(self):
        post = Post.objects.create(
            text='Попадает в кэш',
            author=self.user
        )
        response = self.authorized_client.get(reverse('index'))
        self.assertEqual(response.context.get(
            'page')[0].text,
            'Попадает в кэш'
        )
        post.text = 'Не попадает в кэш'
        post.save()
        self.assertEqual(response.context.get(
            'page')[0].text,
            'Попадает в кэш'
        )

    def test_follow_unfollow(self):
        post = Post.objects.get(author=ViewsTests.user)
        self.auth_client.post(
            reverse('profile_follow',
                    kwargs={'username': self.user.username}), follow=True)
        response_1 = self.auth_client.get(
            reverse('follow_index')
        )
        self.assertContains(response_1, post)
        self.auth_client.post(
            reverse('profile_unfollow',
                    kwargs={'username': self.user.username}), follow=True)
        response_2 = self.auth_client.get(
            reverse('follow_index')
        )
        self.assertNotContains(response_2, post)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='mr.test')

        cls.group = Group.objects.create(
            title='Тестовой группа',
            slug='test-slug')

        objs = [
            Post(
                text='Текстовый пост',
                author=cls.user,
                group=cls.group) for i in range(13)]
        Post.objects.bulk_create(objs)

    def setUp(self):
        self.client = Client()

    def test_first_page_contains_ten_records(self):
        pages = {
            reverse('index'): 10,
            reverse('slug', kwargs={"slug": "test-slug"}): 10,
            reverse('profile', kwargs={'username': self.user.username}): 10,
        }

        for value, expected in pages.items():
            with self.subTest(value=value):
                responce = self.client.get(value)
                self.assertEqual(len(
                    responce.context.get('page').object_list),
                    expected)

    def test_second_page_contains_three_records(self):
        pages = {
            reverse('index'): 3,
            reverse('slug', kwargs={"slug": "test-slug"}): 3,
            reverse('profile', kwargs={'username': self.user.username}): 3,
        }
        for value, expected in pages.items():
            with self.subTest(value=value):
                responce = self.client.get(value + '?page=2')
                self.assertEqual(len(
                    responce.context.get('page').object_list),
                    expected)
