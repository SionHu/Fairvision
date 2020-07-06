import boto3
from botocore.client import Config
from botocore.exceptions import ClientError
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from threading import Lock
import os

mturk = boto3.client('mturk',
    aws_access_key_id = settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key = settings.AWS_SECRET_ACCESS_KEY,
    region_name='us-east-1',
    endpoint_url = settings.MTURK_URL
)

class MediaStorage(FileSystemStorage):
    def __init__(self):
        super().__init__(location='datasets', base_url='/datasets')

from django.core.files.storage import default_storage

class _UploadLock:
    '''
    Used to find out which folder the ImageModelForm is uploading to in S3

    Usage:
    with default_storage.upload_lock(dataset, object):
        ImageModel.objects.create(img=file)

    All 'ImageModel.objects.create' statements within the with block will upload to the correct folder.
    The default folder is 'unknown/unknown'.
    '''

    # Instance initialization
    def __init__(self):
        self._lock = Lock()
        self('unknown', 'unknown')
    #
    def __enter__(self):
        self._lock.acquire()

    def __exit__(self, exc_type, exc_value, tb):
        self._lock.release()

    # Call function that will be called in admin.py
    def __call__(self, dataset, object):
        folder = '%s/%s' % (dataset, object)
        self.key = folder+"/"
        return self
default_storage.upload_lock = _UploadLock()
