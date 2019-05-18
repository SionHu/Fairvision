import boto3
from botocore.client import Config
from botocore.exceptions import ClientError
from django.conf import settings
from storages.backends.s3boto3 import S3Boto3Storage
from threading import RLock
import os

class MediaStorage(S3Boto3Storage):
    location = 'media'
    file_overwrite = False

    s3 = boto3.client('s3', aws_access_key_id=settings.AWS_ACCESS_KEY_ID, aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                      config=Config(s3={'addressing_style': 'path'}), region_name='us-east-2')

    #for some reason, this method is flawed in Django Storages, so this just reimplements it correctly
    def url(self, name, parameters=None, expire=300):
        try:
            params = parameters.copy() if parameters else {}
            params['Bucket'] = self.bucket.name
            params['Key'] = self.location+"/"+name

            return self.s3.generate_presigned_url('get_object', Params=params, ExpiresIn=expire)
        except ClientError as e:
            if e.response['Error']['Code'] == "404":
                print("The object %s does not exist." % name)
                return super().url(name, parameters, expire)
            else:
                raise

from django.core.files.storage import default_storage

class _UploadLock:
    '''
    Used to find out which folder the ImageModelForm is uploading to in S3

    Usage:
    with default_storage.upload_lock(dataset, object):
        ImageModel.objects.create(img=file)

    All 'ImageModel.objects.create' statements within the with block will upload to the correct folder.
    The default folder is 'unknown/unknown'.

    The folder that is being uploaded to can be accessed at default_storage.upload_lock.key.
    The highest indexed image in the folder can be accessed via default_storage.upload_lock.count.

    This also contains an RLock that could shared with multiple threads.

    '''

    # Instance initialization
    def __init__(self):
        self._lock = RLock()
        self('unknown', 'unknown')
    # 
    def __enter__(self):
        self._lock.__enter__()

    def __exit__(self, exc_type, exc_value, tb):
        self._lock.__exit__(exc_type, exc_value, tb)

    # Call function that will be called in admin.py
    def __call__(self, dataset, object):
        folder = '%s/%s' % (dataset, object)
        _, files = default_storage.listdir(folder)
        self.count = int(files[-1][-8:-4]) if files else 0
        self.key = folder+"/"
        return self
default_storage.upload_lock = _UploadLock()
