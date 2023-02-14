import datetime
import io
import os
import json
from urllib import parse

from PIL import Image
import firebase_admin
from firebase_admin import credentials
from firebase_admin import storage

cred = credentials.Certificate(dict(json.loads(os.environ.get('firebase'))))


def initialize_app():
    """
    Firebase is initialized with the credentials stored in the environment
    Firebase credentials are of json type and is stored in environment under key firebase
    :return:
    """
    firebase_admin.initialize_app(credential=cred)
    print('Firebase initialized...')


def process_image(file):
    """
    Function is used to resize the image to 576x200 resolution and in webp extension
    :param file:
    :return: File in BytesIO format
    """
    img = Image.open(file)
    img.resize((576, 200))
    b = io.BytesIO()
    img.save(b, "webp")
    b.seek(0)
    return [file, b]


def upload(file):
    """
    Function to upload file (images and audios) to google storage bucket
    :param file: File object
    :return: String - url of the object in the fire storage
    """
    bucket = storage.bucket(os.environ.get("BUCKET_NAME"))
    if type(file) == list:
        blob = bucket.blob(str(datetime.datetime.now().timestamp()) + "-" + str(file[0].filename).replace(' ', '-'))
        blob.upload_from_file(file_obj=file[1], content_type=file[0].content_type)
        blob.make_public()
        return blob.public_url
    blob = bucket.blob(str(datetime.datetime.now().timestamp()) + "-" + str(file.filename))
    blob.upload_from_file(file_obj=file, content_type=file.content_type)
    blob.make_public()
    return blob.public_url


def deleteBlob(url):
    """
    Function to delete the object
    Deletes object using its basename, the name is retrieved through url

    :param url: string, url of the object present in the bucket
    :return: None
    """
    bucket = storage.bucket(os.environ.get("BUCKET_NAME"))
    blob_name = parse.unquote(parse.urlparse(
        url
    ).path.removeprefix(f'/{os.environ.get("BUCKET_NAME")}/'))
    print(blob_name)
    blob = bucket.get_blob(blob_name)
    if blob and blob.exists():
        print(f"Deleting blob {blob_name}")
        blob.delete()
        return
    print(f"Deleting blob {blob_name}: doesn't exist")
