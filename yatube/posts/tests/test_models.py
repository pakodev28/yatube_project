from django.contrib.auth import get_user_model
from django.test import TestCase

from posts.models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='mr.test')
        cls.post = Post.objects.create(text='тестовый пост' * 5,
                                       author=cls.user,)

    def test_post_text_str_field_len(self):
        post = PostModelTest.post
        text_str_len = len(str(post))
        self.assertEqual(text_str_len, 15, 'Длина не соответсвует 15')

    def test_post_verbose_name(self):
        post = PostModelTest.post
        fields_verbose_names = {
            'text': 'Текст',
            'pub_date': 'Дата публикации поста',
            'author': 'Автор',
            'group': 'Группа'
        }
        for value, expected in fields_verbose_names.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).verbose_name, expected)

    def test_post_help_text(self):
        post = PostModelTest.post
        fields_help_text = {
            'text': 'Введите текст',
            'group': 'Вы можете указать группу'
        }
        for value, expected in fields_help_text.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).help_text, expected)


class GroupModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(title='Тестовая группа')

    def test_group_title_str_field(self):
        group = GroupModelTest.group
        self.assertEqual(str(group), group.title,
                         'Имя группы и значение поля __str__ отличаются')

    def test_post_verbose_name(self):
        group = GroupModelTest.group
        fields_verbose_names = {
            'title': 'Название группы',
            'slug': 'Адресс группы',
            'description': 'Описание'
        }
        for value, expected in fields_verbose_names.items():
            with self.subTest(value=value):
                self.assertEqual(
                    group._meta.get_field(value).verbose_name, expected)

    def test_post_help_text(self):
        group = GroupModelTest.group
        fields_help_text = {
            'title': 'Укажите название группы',
            'slug': 'Укажите адресс группы в интернете',
            'description': 'Дайте подробное описание группы'
        }
        for value, expected in fields_help_text.items():
            with self.subTest(value=value):
                self.assertEqual(
                    group._meta.get_field(value).help_text, expected)
