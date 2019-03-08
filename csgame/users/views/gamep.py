from django.shortcuts import render, redirect
from django.conf import settings
from django.views.generic.edit import CreateView
from django.contrib.auth.decorators import login_required
from ..forms import TestForm
import boto3
import botocore
from botocore.client import Config
import random

basket = {'taboo1', 'taboo2', 'taboo3',}
def handle_ajax(request):
    # test to see if we can get a number of words
    # generate random unique numbers, without any models (First Try)
    data = random.sample(range(121, 800), 4)
    for d in data:
        print("{0:04d}".format(d))
    print("4 random numbers are", data)
    KEY = "airplanes/image_"
    KEY1 = KEY + "{:04d}".format(data[0]) + ".jpg"
    KEY2 = KEY + "{:04d}".format(data[1]) + ".jpg"
    KEY3 = KEY + "{:04d}".format(data[2]) + ".jpg"
    KEY4 = KEY + "{:04d}".format(data[3]) + ".jpg"

    print("Key1: ", KEY1)

    # connect to s3
    s3 = boto3.client('s3', aws_access_key_id=settings.AWS_ACCESS_KEY_ID, aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                  config=Config(s3={'addressing_style': 'path'}), region_name='us-east-2')
    try:
        url1 = s3.generate_presigned_url('get_object',
                                    Params={
                                        'Bucket': settings.AWS_STORAGE_BUCKET_NAME,
                                        'Key': KEY1,
                                    },                                  
                                    ExpiresIn=300)
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == "404":
            print("The object does not exist.")
        else:
            raise
    try:
        url2 = s3.generate_presigned_url('get_object',
                                    Params={
                                        'Bucket': settings.AWS_STORAGE_BUCKET_NAME,
                                        'Key': KEY2,
                                    },                                  
                                    ExpiresIn=300)
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == "404":
            print("The object does not exist.")
        else:
            raise

    try:
        url3 = s3.generate_presigned_url('get_object',
                                    Params={
                                        'Bucket': settings.AWS_STORAGE_BUCKET_NAME,
                                        'Key': KEY3,
                                    },                                  
                                    ExpiresIn=300)
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == "404":
            print("The object does not exist.")
        else:
            raise

    try:
        url4 = s3.generate_presigned_url('get_object',
                                    Params={
                                        'Bucket': settings.AWS_STORAGE_BUCKET_NAME,
                                        'Key': KEY4,
                                    },                                  
                                    ExpiresIn=300)
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == "404":
            print("The object does not exist.")
        else:
            raise

    # print("Url is: ", url)
    if request.method == 'POST':
        form = TestForm(request.POST)

        if form.is_valid():
            input1 = form.cleaned_data['test']
            print("input is:", input1)
            basket.add(input1)
    form = TestForm()
    print("form is: ", form)
    return render(request, 'stjs.html',{'form': form, 'url1': url1, 'url2': url2, 'url3': url3, 'url4': url4, 'dictionary': basket, })