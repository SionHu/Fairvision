import pandas as pd
import shutil
import os
from tqdm import tqdm

category = "dog"
path = "./flickr30k_images/results.csv"  # change path if needed
source = "./flickr30k_images/flickr30k_images/"  # change if needed
dest = category  # create folder first
pattern = "^{}s? | {}s? | {}s?$".format(category, category, category)  # change regex if needed

df = pd.read_csv(path, sep="|", header=0, names=['image_name', 'comment_number', 'comment'])
df['comment'].str.lower()
df.dropna(inplace=True)
df['comment'] = df['comment'].str.replace(r'[^\w\s]+', '')

contain_values = df[df['comment'].str.contains(pattern, regex=True)]
unique_images = contain_values['image_name'].unique()
image_list = unique_images.tolist()

print("number of images:", len(unique_images))

if not os.path.exists(dest):
    os.makedirs(dest)

for image in tqdm(image_list):
	shutil.copy(source + image, dest)
