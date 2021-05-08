import pandas as pd
import shutil
import os
from tqdm import tqdm

######## parameters ########
category = "dog"
in_csv = "/home/fairvision/sites/fairvision.net/datasets/flickr30k_images/results.csv"
img_src = "/home/fairvision/sites/fairvision.net/datasets/flickr30k_images/flickr30k_images/"
dest = category
out_images = dest + "/" + dest
out_csv = dest + "/" + dest + ".csv"
pattern = "^{}s? | {}s? | {}s?$".format(category, category, category)
############################


df = pd.read_csv(in_csv, sep="|", header=0, names=['image_name', 'comment_number', 'comment'])
df['comment'].str.lower()
df.dropna(inplace=True)
df['comment'] = df['comment'].str.replace(r'[^\w\s]+', '')

contain_values = df[df['comment'].str.contains(pattern, regex=True)]
unique_images = contain_values['image_name'].unique()
image_list = unique_images.tolist()

print("number of images:", len(unique_images))

if not os.path.exists(out_images):
    os.makedirs(out_images)

for image in tqdm(image_list):
    shutil.copy(img_src + image, out_images)

contain_values.to_csv(out_csv, index=False)
