import os

from flask import Blueprint
from database import Monuments, MonumentImages, MonumentTranslations

share = Blueprint('share', __name__, url_prefix='/share')


@share.route('/<monument_id>', methods=["GET"])
def share_monument(monument_id):
    monument = Monuments.query.filter_by(monument_id=monument_id).first()
    images = MonumentImages.query.filter_by(monument_id=monument_id).first()
    desc = MonumentTranslations.query.filter_by(monument_id=monument_id, language_code='en').first()
    title = ""
    description = ""
    image = ""
    url = ""

    if monument:
        title = monument.name
        url = f"{os.environ.get('FRONT_END_URL', 'https://proto-scapp.pages.dev')}/monument/{monument_id}"
        if images:
            image = images.image
        if desc:
            description = desc.description

    return f"""
    <html>
        <head>
            <meta property="og:title" content="{title}" />
            <meta property="og:type" content="website" />
            <meta property="og:image" content="{image}" />
            <meta property="og:description" content="{description}" />
            <meta property="og:url" content="{url}" />
        </head>
        <body>
            <script type='text/javascript'>
                window.location.replace('{os.environ.get("FRONT_END_URL", 'https://proto-scapp.pages.dev')}/monument/{monument_id}')
            </script>
        </body>
    </html>
    """
