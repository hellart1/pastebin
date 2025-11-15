from django.test import TestCase
from django.shortcuts import reverse

from paste.models import Paste


# class TestPasteCRUD(TestCase):
#     def setUp(self):
#         self.paste = {
#             'hash': 'test_hash',
#             'expiration_type': '10M',
#         }
#
#         self.paste_model = Paste.objects.create(**self.paste)
#
#     def test_added_paste(self):
#         paste = Paste.objects.get(hash='test_hash')
#         self.assertEqual(paste.expiration_type, '10M')
#
#     def test_paste_detail_view(self):
#         pass


class TestPasteApi(TestCase):

    def test_paste_create(self):
        response = self.client.post(reverse('home'), data={
            'paste_text': 'test_text',
            'expiration_type': '10M'
        })
        self.assertEqual(response.status_code, 200)

        paste = Paste.objects.get(hash=response.data['hash'])

        self.assertEqual(paste.expiration_type, 'N')
