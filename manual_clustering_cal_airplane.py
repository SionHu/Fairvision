import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "csgame.settings")
import django
django.setup()
from django.conf import settings
from users.models import ImageModel

if __name__ == "__main__":
    print(settings.KEY)
    biased_list = [120, 102, 103, 104, 99, 98, 96, 95, 94, 93, 92, 91, 90, 89, 88, 87, 86, 85, 84, 83, 82, 81, 80, 79, 71, 59, 57, 53, 49, 48, 47, 37, 24]
    b_list = [settings.KEY.format(x) for x in biased_list]
    print(b_list)
    lol = ImageModel.objects.filter(img__in=b_list)
    for obj in lol:
        obj.cluster = 'B'
        obj.save()
    # bulk_update only support 2.2 so
    # ImageModel.objects.bulk_update(lol, ['cluster'])
