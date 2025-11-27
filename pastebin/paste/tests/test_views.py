from django.test import SimpleTestCase, TestCase
from django.shortcuts import reverse


class TestHomePage(TestCase):

    def test_homepage_status_code(self):
        response = self.client.get(reverse('home'))

        self.assertEqual(response.status_code, 200)

    def test_homepage_correct_template(self):
        response = self.client.get(reverse('home'))

        self.assertTemplateUsed(response, 'paste/home.html')

    def test_create_paste_and_validate_processing(self):
        # создается обьект в хранилище (-)
        response = self.client.post(reverse('home'), data={
            'paste_text': 'test_text',
            'expiration': 'N',
        })
        self.assertEqual(response.status_code, 302)
