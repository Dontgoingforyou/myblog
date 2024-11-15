from django.test import TestCase
from blog.forms import EmailPostForm, CommentForm, SearchForm


class EmailPostFormTest(TestCase):
    def test_valid_data(self):
        """ Проверка валидности формы """

        form = EmailPostForm(data={
            'name': 'Test User',
            'email': 'test@example.com',
            'to': 'test2@example.com',
            'comments': 'test',
        })
        self.assertTrue(form.is_valid())

    def test_invalid_data(self):
        """ Проверка не валидности формы """

        form = EmailPostForm(data={
            'name': 'Test User',
            'email': 'test@example.com',
        })
        self.assertFalse(form.is_valid())


class CommentFormTest(TestCase):
    def test_valid_data(self):
        """ Проверка валидности формы """

        form = CommentForm(data={
            'name': 'Test User',
            'email': 'test@example.com',
            'body': 'test',
        })
        self.assertTrue(form.is_valid())

    def test_invalid_email(self):
        """ Проверка валидности email """

        form = CommentForm(data={
            'name': 'Test User',
            'email': 'test',
            'body': 'test',
        })
        self.assertFalse(form.is_valid())


class SearchFormTest(TestCase):
    def test_valid_query(self):
        """ Проверка валидности запроса """

        form = SearchForm(data={'query': 'Django'})
        self.assertTrue(form.is_valid())

    def test_empty_query(self):
        """ Проверка пустого запроса """

        form = SearchForm(data={'query': ''})
        self.assertFalse(form.is_valid())