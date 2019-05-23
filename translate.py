# This is the python file that unzip the zip file and enforce to translate the datasets of the file
import zipfile
import os

current_dir = os.path.dirname(os.path.abspath(__file__))

def unzip_topath():
    zip_ref = zipfile.ZipFile()
    zip_ref.close()
    return unzip_path

