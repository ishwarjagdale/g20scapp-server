import datetime
import hashlib
import os

from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user

from api.app import get_monument
from api.storage_api import upload, process_image, deleteBlob
from database import Monuments, MonumentTranslations, MonumentImages, db

admin = Blueprint('admin', __name__, url_prefix='/url_qr/admin')


@admin.route('/new', methods=["POST"])
@login_required
def new_monument():
    payload = request.form.to_dict()

    name = payload['name'].strip()
    monument_id = name.replace(' ', '-') + '-' + str(hashlib.sha256(
        bytes(str(datetime.datetime.now(datetime.timezone.utc).timestamp()), encoding='utf-8')
    ).hexdigest())
    long, lat = payload['longitude'], payload['latitude']

    category = payload['category'].strip().title()
    public = True if payload['makePublic'] == 'true' else False

    if 'id' in payload:
        monument = Monuments.query.filter_by(monument_id=payload['id']).first()
        if monument:
            monument.name = name
            monument.long, monument.lat = long, lat
            monument.category = category
            monument.public = public

            db.session.commit()

            print(current_user.email_addr, "updated monument", monument.monument_id)

    else:
        monument = Monuments(monument_id=monument_id, name=name, long=long, lat=lat, category=category, public=public)
        db.session.add(monument)
        db.session.commit()

        print(current_user.email_addr, "added monument", monument.monument_id)

    return jsonify({"monument_id": monument.monument_id, "message": "monument updated!"}) if 'id' in payload else \
        jsonify({"monument_id": monument.monument_id})


@admin.route('/edit/<monument_id>', methods=["GET"])
@login_required
def get_complete_monument(monument_id):
    monument = Monuments.query.filter_by(monument_id=monument_id).first()

    if not monument:
        return jsonify({"message": "monument not found"}), 404

    images = MonumentImages.query.filter_by(monument_id=monument_id).all()
    descriptions = MonumentTranslations.query.filter_by(monument_id=monument_id).all()

    response = {
        "id": monument.monument_id,
        "name": monument.name,
        "longitude": monument.long,
        "latitude": monument.lat,
        "category": monument.category,
        "images": list(map(lambda x: x.image, images)),
        "descriptions": {},
        "public": monument.public
    }

    for desc in descriptions:
        response["descriptions"][desc.language_code] = {
            "name": desc.name,
            "description": desc.description,
            "audio": desc.audio
        }

    return jsonify(response), 200


@admin.route('/monuments/<monument_id>/images', methods=["POST", "DELETE"])
@login_required
def delete_image(monument_id):
    monument = Monuments.query.filter_by(monument_id=monument_id).first()

    if not monument:
        return jsonify({"message": "monument not found"}), 404

    if request.method == "POST":
        urls = []
        for image in request.files.to_dict():
            if image.startswith('image'):
                img_url = upload(process_image(request.files[image]))
                img = MonumentImages(monument_id=monument.monument_id, image=img_url)
                db.session.add(img)
                urls.append(img_url)
        db.session.commit()

        print(current_user.email_addr, "added images for monument", monument.monument_id)

        return jsonify({"monument_id": monument.monument_id, "message": "image uploaded!", "urls": urls})

    if request.method == "DELETE":
        image = MonumentImages.query.filter_by(monument_id=monument_id, image=request.args['image']).first()
        if image:
            deleteBlob(image.image)
            db.session.delete(image)
            db.session.commit()

            print(current_user.email_addr, "deleted image for monument", monument.monument_id)

            return jsonify({"message": "image deleted"}), 200

        return jsonify({"message": "image not found"}), 404


@admin.route('/monuments/<monument_id>/description', methods=["POST", "DELETE"])
@login_required
def addLanguage(monument_id):
    monument = Monuments.query.filter_by(monument_id=monument_id).first()

    if not monument:
        return jsonify({"message": "monument not found"}), 404

    if request.method == "POST":
        payload = request.form.to_dict()

        translation = MonumentTranslations.query.filter_by(monument_id=monument_id,
                                                           language_code=payload['language']
                                                           ).first()
        if translation:
            if 'audio' in request.files:
                audio = upload(request.files['audio'])
                translation.audio = audio
            translation.name = payload['name']
            translation.description = payload['description']
            try:
                db.session.commit()
            except Exception as e:
                print(e)

            return jsonify({"message": f"{payload['language']} translation updated",
                            "translation": {
                                "code": translation.language_code,
                                "name": translation.name,
                                "description": translation.description,
                                "audio": translation.audio
                            }
                            }), 200
        else:
            audio = request.files.get('audio', None)
            if audio:
                audio = upload(audio)
            translation = MonumentTranslations(
                monument_id=monument.monument_id,
                language_code=payload['language'],
                name=payload['name'],
                description=payload['description'],
                audio=audio
            )
            db.session.add(translation)
            db.session.commit()

            print(current_user.email_addr, "added translation", payload['language'], "for", monument.monument_id)

            return jsonify({"message": f"{payload['language']} translation added"}), 200

    if request.method == "DELETE":
        translation = MonumentTranslations.query.filter_by(monument_id=monument_id,
                                                           language_code=request.args['lang']
                                                           ).first()
        if not translation:
            return jsonify({"message": f"{request.args['lang']} translation not found"}), 404

        db.session.delete(translation)
        db.session.commit()

        print(current_user.email_addr, "deleted translation", request.args['lang'], "for", monument.monument_id)

        return jsonify({"message": f"{request.args['lang']} translation deleted"}), 200


@admin.route('/monuments', methods=["GET"])
@login_required
def getAllMonuments():
    response = []
    query = Monuments.query.all()
    for monument in query:
        response.append(get_monument(monument, 'en'))

    return jsonify({"response": response})


@admin.route('/monuments/<monument_id>', methods=["DELETE"])
@login_required
def delete_monument(monument_id):
    monument = Monuments.query.filter_by(monument_id=monument_id).first()

    if monument:
        images = MonumentImages.query.filter_by(monument_id=monument_id).all()
        for img in images:
            if img.image:
                deleteBlob(img.image)
        translation = MonumentTranslations.query.filter_by(monument_id=monument_id).all()
        for desc in translation:
            if desc.audio:
                deleteBlob(desc.audio)

        db.session.delete(monument)
        db.session.commit()

        print(current_user.email_addr, "deleted monument", monument_id)

        return jsonify({"message": f"{monument.monument_id} deleted"}), 200

    return jsonify({"message": "monument not found"}), 404
