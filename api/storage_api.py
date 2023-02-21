import datetime
import io
import os
from flask import current_app
from PIL import Image
from werkzeug.datastructures import FileStorage


def process_image(file):
    img = Image.open(file)
    img.resize((576, 200))
    b = io.BytesIO()
    img.save(b, "webp")
    b.seek(0)
    return FileStorage(b, file.filename, content_type='image/webp', content_length=file.content_length)


def upload(file):
    if not os.path.exists(current_app.config.get("STORAGE")):
        os.makedirs(current_app.config.get("STORAGE"))

    file_name = str(datetime.datetime.now().timestamp()) + "-" + str(file.filename)
    file.save(os.path.join(current_app.config.get("STORAGE"), file_name))
    return os.path.join(current_app.config.get("STORAGE"), file_name)


def deleteBlob(url):
    if os.path.exists(url) and os.path.isfile(url):
        print(f"Deleting file {url}")
        os.remove(url)
        return
    print(f"Deleting file {url}: doesn't exist")
