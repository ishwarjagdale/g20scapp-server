import datetime
import io
import os
import json
from PIL import Image
import firebase_admin
from firebase_admin import credentials
from firebase_admin import storage

cred = credentials.Certificate(dict(json.loads(os.environ.get('firebase'))))


def initialize_app():
    firebase_admin.initialize_app(credential=cred)
    print('Firebase initialized...')


def process_image(file):
    img = Image.open(file)
    img.resize((576, 200))
    b = io.BytesIO()
    img.save(b, "webp")
    b.seek(0)
    return [file, b]


def upload(file):
    bucket = storage.bucket('g20scapp.appspot.com')
    if type(file) == list:
        blob = bucket.blob(str(datetime.datetime.now().timestamp()) + str(file[0].filename))
        blob.upload_from_file(file_obj=file[1], content_type=file[0].content_type)
        blob.make_public()
        return blob.public_url
    blob = bucket.blob(str(datetime.datetime.now().timestamp()) + str(file.filename))
    blob.upload_from_file(file_obj=file, content_type=file.content_type)
    blob.make_public()
    return blob.public_url


def deleteBlob():
    bucket = storage.bucket('g20scapp.appspot.com')