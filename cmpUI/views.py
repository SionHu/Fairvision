from django.shortcuts import render
from django.http import HttpResponse
import random
from django.conf import settings
from cmpUI.models import ImageModel

IMG_Dataset = ['Caltech101', 'ImageNet', 'COCO', 'VOC', 'SUN']

# Create your views here.
def img_test(request):
    # dataset = random.choice(IMG_Dataset)
    dataset = IMG_Dataset[0]
    KEYRING = dataset + '/' + settings.OBJECT_NAME_PLURAL
    # random select given dataset name, object name
    imgurl = ImageModel.objects.filter(img__startswith=KEYRING).order_by("?").first()
    return render(request, 'test.html', {'imgurl': imgurl.img.url, 'datasetName': dataset, 'ObjectName': settings.OBJECT_NAME_PLURAL})
