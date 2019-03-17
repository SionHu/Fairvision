from django.shortcuts import render, redirect
from django.conf import settings
from django.views.generic.edit import CreateView
from django.contrib.auth.decorators import login_required

from users.models import ImageModel, Label

# from ..forms import TestForm
import boto3
import botocore
from botocore.client import Config
import random

import json

@login_required
def handle_ajax(request):
    # Some test
    # idk = ImageModel.objects.get(img='airplanes/image_0053.jpg')
    # print(idk.label.all())

    data = random.sample(range(1, 121), 4)
    print("4 random numbers are", data)
    
    KEY = "media/airplanes/image_"
    KEYS = [KEY] * 4
    for x in range(0, 4):
        KEYS[x] += "{:04d}".format(data[x]) + ".jpg"

    # print("KEYS: ", KEYS)

    urls = list()

    for k in KEYS:
        # connect to s3
        s3 = boto3.client('s3', aws_access_key_id=settings.AWS_ACCESS_KEY_ID, aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                      config=Config(s3={'addressing_style': 'path'}), region_name='us-east-2')
        try:
            url = s3.generate_presigned_url('get_object',
                                        Params={
                                            'Bucket': settings.AWS_STORAGE_BUCKET_NAME,
                                            'Key': k,
                                        },                                  
                                        ExpiresIn=300)
        except botocore.exceptions.ClientError as e:
            if e.response['Error']['Code'] == "404":
                print("The object does not exist.")
            else:
                raise
        urls.append(url)

    # print("Url is: ", urls)


    if request.method == 'POST':
        data = request.POST.getlist('data[]')
#        print("I got data: ", data)
        img_list = request.POST.getlist('img_list[]')
#        print("I got the image num: ", img_list)
        key = "airplanes/image_"
        # Search fo r 
        for il in img_list:
            update_img = key + "{:04d}".format(int(il)) + ".jpg"
            print("the label need to be stored in: ", update_img)
            model = ImageModel.objects.filter(img=update_img).first()
            if model:
                for d in data:
                    d = d.lower()
                    # print("Lower case: ", d)
                    # first iterate through whole label list
                    label = Label.objects.filter(name=d).first()
                    if label:
                    #    print("The exsiting label is: ", label)
                        # check if the image model contains that label
                        lb = model.label.filter(name=d).first()
                        if lb:
                            pass
                        else:
                            model.label.add(label)
                    else:
                        label = Label.objects.create(name=d, isTaboo=False)
                        label.save()
                        model.label.add(label)
            else:
                print("not Found!")
        '''
        imgs = ImageModel.objects.all()
        for i in imgs:
            print("the name of each image is: ", i.img.name)
        '''
    # form = TestForm()
    json_list = json.dumps(data)
    return render(request, 'phase01.html',{ 'url1': urls[0], 'url2': urls[1], 'url3': urls[2], 'url4': urls[3], 'json_list': json_list, })

