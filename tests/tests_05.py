from django.conf import settings
from time import sleep
from django.contrib.auth import get_user_model
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from posts.models import Group, Post

User = get_user_model()


class TestPosts(TestCase):

    def setUp(self):
        self.client = Client()

        self.user = User.objects.create_user(username='user', password='pass')
        self.user.save()
        self.client.login(username='user', password='pass')

        self.group = Group.objects.create(
            title='group of users',
            slug='groupofusers',
            description='test group'
        )

        self.text = "Lorem ipsum dolor sit amet, consectetur adipiscing"
        self.text_edited = f'edited {self.text}'

    def response_get(self, name, rev_args=None, followed=True):
        return self.client.get(
            reverse(
                name,
                kwargs=rev_args
            ),
            follow=followed
        )

    def response_post(self, name, post_args=None, rev_args=None, fol=True):
        return self.client.post(
            reverse(
                name,
                kwargs=rev_args
            ),
            data=post_args,
            follow=fol
        )

    def test_profile_exist(self):
        """Проверка наличия профиля созданного пользователя"""
        response = self.response_get(
            name='profile',
            rev_args={'username': self.user.username}
        )
        self.assertEqual(response.status_code, 200)

    def test_auth_new_post(self):
        """Проверка возможности создания новой публикации
        авторизованным пользователем
        """
        response = self.response_post(
            name='new_post',
            post_args={'text': self.text, 'group': self.group.id}
        )
        self.assertEqual(response.status_code, 200)
        post = Post.objects.get(author=self.user)
        self.assertEqual(post.text, self.text)

    def test_not_auth_new_post(self):
        """ Проверка невозможности создания новой публикации
        неавторизованным пользователем
        """
        self.client.logout()
        response = self.response_post(
            name='new_post',
            post_args={'text': self.text, 'group': self.group.id}
        )

        self.assertRedirects(
            response,
            f"{settings.LOGIN_URL}?next={reverse('new_post')}"
        )

    def test_new_post(self):
        """Проверка наличия созданного поста на главной,
        в профиле, на странице поста.
        """
        self.post = Post.objects.create(
            text=self.text,
            author=self.user
        )

        response = self.response_get(name='index')
        self.assertIn(self.post, response.context['paginator'].object_list)

        response = self.response_get(
            name='profile',
            rev_args={'username': self.user.username}
        )
        self.assertEqual(response.context['post'], self.post)

        response = self.response_get(
            name='post',
            rev_args={
                'username': self.user.username,
                'post_id': self.post.id
            }
        )
        self.assertEqual(response.context['post'], self.post)

    @override_settings(
        CACHES={
            'default': {
                'BACKEND': 'django.core.cache.backends.dummy.DummyCache'
            }
        }
    )
    def test_edit(self):
        """Редактирование авторизованным пользователем поста и
        проверка изменения на связанных страницах.
        """
        post = Post.objects.create(text=self.text, author=self.user)

        self.response_post(
            name='post_edit',
            rev_args={
                'username': self.user.username,
                'post_id': post.id
            },
            post_args={'text': self.text_edited}
        )

        # Проверка редактирования поста
        post.refresh_from_db()
        self.assertEqual(self.text_edited, post.text)

        # Проверка поста на связанных страницах
        params = [
            ('index', None),
            ('profile', {'username': self.user.username}),
            ('post', {'username': self.user.username, 'post_id': post.id})
        ]
        for name, rev_args in params:
            with self.subTest():
                response = self.response_get(name, rev_args)
                self.assertContains(response, self.text_edited)
