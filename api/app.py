from flask import Blueprint, jsonify, request
from database import Monuments, MonumentImages, MonumentTranslations

api = Blueprint('api', __name__, url_prefix='/api')


def get_monument(monument, code, detailed=False):
    images = []
    translation = MonumentTranslations.query.filter_by(monument_id=monument.monument_id, language_code=code).first()
    if not translation:
        translation = MonumentTranslations.query.filter_by(monument_id=monument.monument_id, language_code='en').first()
    temp = MonumentImages.query.filter_by(monument_id=monument.monument_id)

    if detailed:
        images.extend(list(map(lambda x: x.image, temp.all())))
    else:
        temp = temp.first()
        if temp:
            images.append(temp.image)

    resp = {
        "id": monument.monument_id,
        "name": translation.name if translation else monument.name,
        "images": images,
        "long": monument.long,
        "lat": monument.lat,
    }

    if detailed:
        resp["description"] = translation.description if translation else None
        resp["audio"] = translation.audio

    return resp


@api.route('/<language>/populars', methods=["GET"])
def get_populars(language):
    response = []
    query = Monuments.query.order_by(Monuments.views).limit(3).all()
    for monument in query:
        # translation = MonumentTranslations.query.filter_by(monument_id=monument.monument_id,
        # language_code=language).first() image = MonumentImages.query.filter_by(
        # monument_id=monument.monument_id).first() response.append({ "name": translation.name or monument.name,
        # "image": image.image, "long": monument.long, "lat": monument.lat
        #
        # })
        response.append(get_monument(monument, language))
    return jsonify({"status": 200, "response": response})


@api.route('/<language>/categories', methods=["GET"])
def get_categories(language):
    response = {}

    for cat, in Monuments.query.with_entities(Monuments.category).distinct():
        response[cat] = []
        for mon in Monuments.query.filter_by(category=cat).limit(3).all():
            response[cat].append(get_monument(monument=mon, code=language))

    return jsonify({"status": 200, "response": response})


@api.route('/<language>/categories/<category>', methods=["GET"])
def get_category(language, category):
    response = []
    category = category.replace('-', ' ').title()
    for mon in Monuments.query.filter_by(category=category).all():
        response.append(get_monument(monument=mon, code=language))

    return jsonify({"status": 200, "response": response})


@api.route('/<language>/monument/<monument_id>', methods=["GET"])
def get_monument_view(language, monument_id):
    mon = Monuments.query.filter_by(monument_id=monument_id).first()
    response = get_monument(monument=mon, code=language, detailed=bool(request.args.get('detailed')))
    return jsonify({"status": 200, "response": response})


@api.route('/<language>/monuments', methods=["POST"])
def get_monuments(language):
    response = []
    print(request.json)
    for monID in request.json:
        mon = Monuments.query.filter_by(monument_id=monID).first()
        if mon:
            response.append(get_monument(monument=mon, code=language, detailed=False))

    return jsonify({"status": 200, "response": response})
