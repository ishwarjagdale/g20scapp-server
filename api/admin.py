import datetime
import hashlib
import json

from flask import Blueprint, request, jsonify, make_response
from flask_login import login_required
from api.app import get_monument
from api.fire_storage import upload
from database import Monuments, MonumentTranslations, MonumentImages, db

admin = Blueprint('admin', __name__, url_prefix='/admin')


@admin.route('/new', methods=["POST"])
@login_required
def new_monument():
    payload = request.form.to_dict()
    payload['descriptions'] = json.loads(payload['descriptions'])

    name = payload['name'].strip()
    monument_id = name.replace(' ', '-') + '-' + str(hashlib.sha256(
        bytes(str(datetime.datetime.now(datetime.timezone.utc).timestamp()), encoding='utf-8')
    ).hexdigest())
    coordinates = payload['coordinates'].strip()
    if ',' in coordinates:
        long, lat = map(lambda x: x.strip(), coordinates.split(','))
    else:
        long, lat = None, None

    category = payload['category'].strip().title()

    monument = Monuments(monument_id=monument_id, name=name, long=long, lat=lat, category=category)
    db.session.add(monument)
    db.session.commit()

    for desc in payload['descriptions']:
        translation = MonumentTranslations(
            monument_id=monument.monument_id,
            language_code=desc,
            name=payload['descriptions'][desc]['name'],
            description=payload['descriptions'][desc]['description'],
            audio=payload['descriptions'][desc].get('audio', None)
        )
        db.session.add(translation)
    db.session.commit()

    for image in upload(request.files.to_dict()):
        img = MonumentImages(monument_id=monument.monument_id, image=image)
        db.session.add(img)
    db.session.commit()

    return jsonify({"monument_id": monument.monument_id})


@admin.route('/monuments', methods=["GET"])
@login_required
def getAllMonuments():
    response = []
    query = Monuments.query.all()
    for monument in query:
        response.append(get_monument(monument, 'en'))

    return jsonify({"response": response})
