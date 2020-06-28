from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Group(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField()

    def __str__(self):
        return f'{self.title} - {self.slug}'


class Post(models.Model):
    text = models.TextField()
    pub_date = models.DateTimeField('date published', auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name='posts')
    group = models.ForeignKey(Group, on_delete=models.SET_NULL, blank=True,
                              null=True, related_name='posts')
    image = models.ImageField(upload_to='posts/', blank=True, null=True)

    def __str__(self):
        return f'{self.text[:50]} - {self.pub_date}'

    class Meta:
        ordering = ['-pub_date']


class Comment(models.Model):
    post = models.ForeignKey(
        Post,
        related_name='comments',
        on_delete=models.CASCADE
    )
    author = models.ForeignKey(
        User,
        related_name='comments',
        on_delete=models.SET_NULL,
        null=True
    )
    text = models.TextField()
    created = models.DateTimeField('date published', auto_now_add=True)

    class Meta:
        ordering = ['-created']

    def __str__(self):
        return f"Запись: '{self.post}', автор: '{self.author}'"


class Follow(models.Model):
    # пользователь, который подписывается
    user = models.ForeignKey(
        User,
        related_name='follower',
        on_delete=None
    )
    # пользователь, на которого подписывются
    author = models.ForeignKey(
        User,
        related_name='following',
        on_delete=models.CASCADE
    )

    def __str__(self):
        return f"Последователь: '{self.user}', автор: '{self.author}'"
