from django.test import TestCase
from ..forms import TextForm


class TextFormTest(TestCase):

    def test_valid_form(self):
        form = TextForm({
            'paste_text': 'test_text',
            'expiration': 'test_expiration',
        })

        self.assertTrue(form.is_valid())
