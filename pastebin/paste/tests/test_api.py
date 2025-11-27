from rest_framework.test import APITestCase, APIClient
from django.urls import reverse
from ..models import Paste
from ..serializers import PasteSerializer

class PasteAPITest(APITestCase):
    def setUp(self):
        self.paste = Paste.objects.create(
            hash='test',
            expiration_type='N',
        )
        self.client = APIClient()

    def test_get_paste_api(self):
        url = reverse('paste_api', kwargs={'hash': self.paste.hash})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertIn('hash', response.data)
        self.assertIn('expiration_type', response.data)
        self.assertIn('download_url', response.data)

    def test_get_nonexistent_paste(self):
        url = reverse('paste_api', kwargs={'hash': 'not_found'})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 404)

    # def test_get_paste(self):
    #     serializer = PasteSerializer(data={
    #         'hash': 'test',
    #         'expiration_type': 'N'
    #     }, context={'download_url': 'test_url'})
    #
    #     serializer.is_valid()
    #     result = serializer.validated_data
    #
    #     # self.assertEqual(result.status_code, 200)
    #     self.assertEqual(result['hash'], 'test')
