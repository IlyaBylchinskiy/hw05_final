from time import sleep

from django.contrib.auth import get_user_model
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from posts.models import Group, Post

User = get_user_model()


class posts_test(TestCase):

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

    def test_wrong_url(self):
        """ Возвращение 404, если страница не найдена.
        """
        response = self.client.get('/someurl', follow=True)
        self.assertEqual(response.status_code, 404)

    @override_settings(
        CACHES={
            'default': {
                'BACKEND': 'django.core.cache.backends.dummy.DummyCache'
            }
        }
    )
    def test_post_img(self):
        """ Проверка наличия <img> на странице записи, профиля,
            главной, группы.
        """
        with open('media/posts/test.jpg', 'rb') as img:
            response = self.response_post(
                    name='new_post',
                    post_args={
                        'group': self.group.id,
                        'text': self.text,
                        'image': img
                    }
                )

        params = [
            ('post', {'post_id': 1, 'username': self.user.username}),
            ('index', None),
            ('profile', {'username': self.user.username}),
            ('group_posts', {'slug': self.group.slug})
        ]

        for name, rev_args in params:
            with self.subTest():
                response = self.response_get(name, rev_args)
                self.assertContains(response, '<img')

    def test_not_image_post(self):
        """ Проверка защиты от загрузки файлов неграфических форматов.
        """
        post = Post.objects.create(text='sometext', author=self.user)
        with open('media/posts/notimage.txt', 'rb') as img:
            response = self.response_post(
                    name='post_edit',
                    rev_args={
                        'username': self.user.username,
                        'post_id': post.id
                    },
                    post_args={
                        'author': self.user,
                        'text': self.text_edited,
                        'image': img
                    }
            )
        error_text = ('Загрузите правильное изображение. Файл, который вы '
                      'загрузили, поврежден или не является изображением.')
        self.assertFormError(response, 'form', 'image', error_text)

    def test_cache(self):
        """ Проверка работы кэширования главной страницы. """
        response_before = self.response_get(
            name='index'
        )
        Post.objects.create(text='sometext', author=self.user)
        response_after = self.response_get(name='index')
        self.assertEqual(response_before.content, response_after.content)

        sleep(21)
        response = self.response_get(name='index')
        self.assertNotEqual(response_before.content, response.content)
