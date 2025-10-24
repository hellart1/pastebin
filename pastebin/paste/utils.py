import os
from datetime import timedelta, datetime

import boto3
from botocore.exceptions import ClientError
from django.conf import settings
from django.views.generic.detail import SingleObjectMixin
from rest_framework.response import Response


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
            self, object_name, expiration=None, client=None, bucket_name=settings.AWS_STORAGE_BUCKET_NAME
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


class PasteExpirationMixin(S3UtilsMixin):
    def expiration_handler(self, obj):
        handlers = {
            'N': self.handler_never_expire,
            'B': self.handler_burn_after_read,
            '10M': self.handler_timed_expire,
            '1H': self.handler_timed_expire,
            '1D': self.handler_timed_expire
        }

        handler = handlers.get(obj.expiration_type)
        if handler:
            return handler(obj)

    def handler_never_expire(self, obj):
        return self.create_presigned_url(object_name=obj.hash)

    def handler_burn_after_read(self, obj):
        pass

    def handler_timed_expire(self, obj):
        expiration_delta = {
            '10M': timedelta(minutes=10),
            '1H': timedelta(hours=1),
            '1D': timedelta(days=1),
        }

        expiration = expiration_delta[obj.expiration_type].total_seconds()

        # идея: подключить redis для кэширования ссылки вместо постоянного запроса новой
        time_now = datetime.now().timestamp()
        created_time = obj.created_at.timestamp()

        if time_now < (created_time + expiration):
            lifespan_remain = created_time + expiration - time_now
            return self.create_presigned_url(
                object_name=obj,
                expiration=lifespan_remain
            )
        else:
            print('Срок действия пасты истек')
            return Response(status=404)

    def get_expiration_seconds(self, obj):
        expiration_delta = {
            '10M': timedelta(minutes=10),
            '1H': timedelta(hours=1),
            '1D': timedelta(days=1),
        }
        expiration = expiration_delta[obj.expiration_type]

        created_time = obj.created_at.timestamp()
        time_now = datetime.now().timestamp()

        return created_time + expiration.total_seconds() - time_now



    # def check_expired(self, obj):
    #     expiration_delta = {
    #         '10M': timedelta(minutes=10),
    #         '1H': timedelta(hours=1),
    #         '1D': timedelta(days=1),
    #     }
    #     if obj.expiration_type == 'N':
    #         return None
    #     elif obj.expiration_type == 'B':
    #         return None
    #     expiration = expiration_delta[obj.expiration_type]
    #
    #     # идея: подключить redis для кэширования ссылки вместо постоянного запроса новой
    #     time_now = datetime.now().timestamp()
    #     created_time = (obj.created_at + expiration).timestamp()
    #     if time_now < created_time:
    #         return self.get_expiration_seconds(obj)


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
