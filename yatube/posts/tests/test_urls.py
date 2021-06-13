from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post

User = get_user_model()


class URLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='mr.test')
        cls.user_1 = User.objects.create_user(username='mrs.test')
        cls.group = Group.objects.create(title='Тестовая группа!',
                                         slug='test-slug',
                                         description='Это тестовая группа',
                                         )
        cls.post = Post.objects.create(text='Тестовый пост!', author=cls.user)
        cls.group_adress = f'/group/{cls.group.slug}/'
        cls.profile_adress = f'/{cls.user.username}/'
        cls.post_adress = f'/{cls.user.username}/{cls.post.id}/'
        cls.post_edit_adress = f'/{cls.user.username}/{cls.post.id}/edit/'

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(URLTests.user)
        self.authorized_client_1 = Client()
        self.authorized_client_1.force_login(URLTests.user_1)

    def test_avaliable_for_unauthorized_user(self):
        urls = [
            '/',
            URLTests.group_adress,
            URLTests.profile_adress,
            URLTests.post_adress,
        ]
        for url in urls:
            with self.subTest(url=url):
                response = self.guest_client.get(url, follow=True)
                self.assertEqual(response.status_code, 200)

    def test_avaliable_for_post_author_authorized_user(self):
        urls = [
            '/',
            URLTests.group_adress,
            URLTests.profile_adress,
            URLTests.post_adress,
            '/new/',
            URLTests.post_edit_adress
        ]
        for url in urls:
            with self.subTest(url=url):
                response = self.authorized_client.get(url, follow=True)
                self.assertEqual(response.status_code, 200)

    def test_edit_post_avaliable_for_not_author_authorized_user(self):
        response = self.authorized_client_1.get(URLTests.post_edit_adress)

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, URLTests.post_adress)

    def test_edit_post_avaliable_for_unauthorized_user(self):
        response = self.guest_client.get(URLTests.post_edit_adress)

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/auth/login/?next=/mr.test/1/edit/')

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            '/': 'index.html',
            '/new/': 'new_post.html',
            URLTests.group_adress: 'group.html',
            URLTests.post_edit_adress: 'new_post.html'
        }
        for url, template in templates_url_names.items():
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertTemplateUsed(response, template)

    def test_avaliable_follow_unfollow(self):
        response_1 = self.authorized_client.post(
            reverse('profile_follow',
                    kwargs={'username': self.user_1.username}))
        self.assertEqual(response_1.status_code, 302)
        response_2 = self.authorized_client.get(reverse('follow_index'))
        self.assertEqual(response_2.status_code, 200)
        response_3 = self.authorized_client.post(
            reverse('profile_unfollow',
                    kwargs={'username': self.user_1.username}))
        self.assertEqual(response_3.status_code, 302)

    def test_add_comment_for_authorized_and_guest(self):
        response_1 = self.authorized_client_1.post(
            reverse('add_comment', kwargs={
                    'post_id': self.post.id,
                    'username': self.user.username})
        )
        self.assertEqual(response_1.status_code, 302)
        self.assertRedirects(response_1, reverse(
            'post', kwargs={
                'post_id': self.post.id,
                'username': self.user.username})
        )
        response_2 = self.guest_client.post(
            reverse('add_comment', kwargs={
                    'post_id': self.post.id,
                    'username': self.user.username})
        )
        self.assertEqual(response_2.status_code, 302)
        self.assertRedirects(response_2,
                             '/auth/login/?next=/mr.test/1/comment/')

    def test_page_not_found_404(self):
        '''Возвращает ли сервер код 404, если страница не найдена'''
        response = self.guest_client.get('/mr.fake/')
        self.assertEqual(response.status_code, 404)
