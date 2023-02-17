from flask import Blueprint, jsonify, request
from database import Monuments, MonumentImages, MonumentTranslations, db
from math import radians, cos, sin, asin, sqrt

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

    languages = list(map(lambda x: x[0],
                         MonumentTranslations.query.with_entities(MonumentTranslations.language_code
                                                                  ).filter_by(monument_id=monument.monument_id
                                                                              ).distinct()))

    resp = {
        "id": monument.monument_id,
        "name": translation.name if translation else monument.name,
        "images": images,
        "long": monument.long,
        "lat": monument.lat,
        "languages": languages,
        "category": monument.category
    }

    if detailed:
        resp["description"] = translation.description if translation else None
        resp["audio"] = translation.audio

    return resp


@api.route('/<language>/populars', methods=["GET"])
def get_populars(language):
    response = []
    query = Monuments.query.order_by(Monuments.views).desc().limit(3).all()
    for monument in query:
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

    if bool(request.args.get('detailed')):
        mon.views += 1
        db.session.commit()

    return jsonify({"status": 200, "response": response})


@api.route('/<language>/monuments', methods=["POST"])
def get_monuments(language):
    response = []
    for monID in request.json:
        mon = Monuments.query.filter_by(monument_id=monID).first()
        if mon:
            response.append(get_monument(monument=mon, code=language, detailed=False))

    return jsonify({"status": 200, "response": response})


# Python 3 program to calculate Distance Between Two Points on Earth
# FROM Geeks for Geeks
def distance(lat1, lon1, lat2, lon2):
    # The math module contains a function named
    # radians which converts from degrees to radians.
    lon1 = radians(lon1)
    lon2 = radians(lon2)
    lat1 = radians(lat1)
    lat2 = radians(lat2)

    # Haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2

    c = 2 * asin(sqrt(a))

    # Radius of earth in kilometers. Use 3956 for miles
    r = 6371

    # calculate the result
    return c * r


@api.route('/nearby', methods=["POST"])
def get_nearby_location():
    """
    Function returns response with all the monuments under 5KM range from the coordiantes recieved from the request
    :return:
    """
    print(request.json)
    long, lat = float(request.json['longitude']), float(request.json['latitude'])
    print(lat, long)
    response = []
    query = Monuments.query.all()
    for mon in query:
        if mon.lat > 0 and mon.long > 0:
            if distance(lat, long, mon.lat, mon.long) < 5:
                response.append(get_monument(mon, 'en'))
    print(response)

    return jsonify({"status": 200, "response": response})
