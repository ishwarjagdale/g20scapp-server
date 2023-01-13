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


def upload(files):
    bucket = storage.bucket('g20scapp.appspot.com')
    urls = []
    for file in files:
        blob = bucket.blob(str(datetime.datetime.now().timestamp()) + str(files[file].filename))
        img = Image.open(files[file])
        img.resize((576, 200))
        b = io.BytesIO()
        img.save(b, "webp")
        b.seek(0)
        blob.upload_from_file(file_obj=b, content_type=f'image/{files[file].filename.split(".").pop()}')
        blob.make_public()
        urls.append(blob.public_url)
    return urls
