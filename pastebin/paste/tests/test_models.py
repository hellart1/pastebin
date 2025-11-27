from django.test import TestCase
from paste.models import Paste


class PasteTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.paste = Paste.objects.create(hash='test_text', expiration_type='N')

    def test_paste_is_created(self):
        self.assertEqual(str(self.paste), 'test_text')

