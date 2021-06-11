from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Group(models.Model):
    title = models.CharField(verbose_name='Название группы',
                             help_text='Укажите название группы',
                             max_length=200, null=False)
    slug = models.SlugField(verbose_name='Адресс группы',
                            help_text='Укажите адресс группы в интернете',
                            max_length=100, unique=True)
    description = models.TextField(verbose_name='Описание',
                                   help_text='Дайте подробное описание группы',
                                   null=True, blank=True)

    def __str__(self):
        return self.title


class Post(models.Model):
    text = models.TextField(verbose_name='Текст',
                            help_text='Введите текст')
    pub_date = models.DateTimeField(verbose_name='Дата публикации поста',
                                    auto_now_add=True)
    author = models.ForeignKey(User,
                               verbose_name='Автор',
                               on_delete=models.CASCADE,
                               related_name='user_posts')
    group = models.ForeignKey(Group, verbose_name='Группа',
                              help_text='Вы можете указать группу',
                              on_delete=models.SET_NULL, null=True,
                              blank=True, related_name='group_posts')
    image = models.ImageField(upload_to='posts/', blank=True, null=True)

    class Meta:
        ordering = ['-pub_date']

    def __str__(self):
        return self.text[:15]


class Comment(models.Model):
    post = models.ForeignKey(Post, verbose_name='Пост',
                             on_delete=models.CASCADE,
                             related_name='comments')
    author = models.ForeignKey(User, verbose_name='Автор',
                               on_delete=models.CASCADE,
                               related_name='comments')
    text = models.TextField(max_length=400,
                            verbose_name='Комментарий',
                            help_text='Оставьте свой комментарий')
    created = models.DateTimeField(verbose_name='Дата создания комментария',
                                   auto_now_add=True)


class Follow(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name="follower")
    author = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name="following")
