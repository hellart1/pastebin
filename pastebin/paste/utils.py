import os

import boto3
from botocore.exceptions import ClientError
from django.conf import settings
from django.views.generic.detail import SingleObjectMixin


class S3ConnectMixin:
    def s3_client(self):
        return boto3.client(
            's3',
            endpoint_url=os.getenv("AWS_S3_ENDPOINT_URL"),
            region_name=os.getenv("ru-central1"),
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
        )

    def s3_resource(self):
        return boto3.resource(
            's3',
            endpoint_url=os.getenv("AWS_S3_ENDPOINT_URL"),
            region_name=os.getenv("ru-central1"),
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
        )


class S3UtilsMixin(S3ConnectMixin):

    def put_object_in_s3(self, file_hash, text, resource=None, bucket_name=settings.AWS_STORAGE_BUCKET_NAME):
        resource = resource or self.s3_resource()
        bucket = resource.Bucket(bucket_name)
        try:
            return bucket.put_object(
                Key=f"{file_hash}.txt",
                Body=text
            )
        except Exception as e:
            print(f"Ошибка: {e}")
            return None

    def create_presigned_url(
            self, object_name, client=None, bucket_name=settings.AWS_STORAGE_BUCKET_NAME, expiration=None
    ):
        client = client or self.s3_client()
        print(client)
        print(object_name)
        try:
            return client.generate_presigned_url(
                ClientMethod='get_object',
                Params={'Bucket': bucket_name, 'Key': f"{object_name}.txt"},
                ExpiresIn=expiration
            )

        except ClientError as e:
            print("ошибка клиента")
            # logging.error(e)
            return None

# class StrObjectMixin(SingleObjectMixin):
#     str_field = 'data'
#
#     def get_object(self, queryset=None):
#         if queryset is None:
#             queryset = self.get_queryset()
#
#         str = self.kwargs.get(self.str_field)
#
#         if not str:
#             raise AttributeError("Str is required to get an object")
#
#         return queryset.filter(**{self.str_field: str}).get()
