from django.urls import reverse, resolve
from django.test import SimpleTestCase
from ..views import Home, User_text

class UrlTest(SimpleTestCase):

    def test_home_url_resolves(self):
        url = reverse('home')
        self.assertEqual(resolve(url).func.view_class, Home)

    def test_user_text_url_resolves(self):
        url = reverse('user_text', kwargs={'data': 'test'})
        self.assertEqual(resolve(url).func.view_class, User_text)