import os
import json
import re

from dotenv import load_dotenv
from slugify import slugify

MAX_SLUG_LENGTH = 100
ARTICLE_FIELDS_TO_SAVE = ['header', 'signature', 'body', 'user_id']

load_dotenv()
articles_dir = os.environ.get('ARTICLES_DIR')
articles_ext = os.environ.get('ARTICLES_EXT')


def get_slug(header):
    slug = slugify(header, max_length=MAX_SLUG_LENGTH) + '_1'
    filename = f'{slug}{articles_ext}'
    while os.path.exists(os.path.join(articles_dir, filename)):
        filename_base, filename_num = filename[:-len(articles_ext)].split('_')
        slug = f'{filename_base}_{int(filename_num) + 1}'
        filename = f'{slug}{articles_ext}'
    return slug


def clean_data(data):
    data.fromkeys(ARTICLE_FIELDS_TO_SAVE)
    return data


def read_article(slug):
    try:
        filepath = os.path.join(articles_dir, f'{slug}{articles_ext}')
        with open(filepath) as file:
            return json.loads(file.read())
    except FileNotFoundError:
        abort(404)


def write_article(slug, data, session):
    data['user_id'] = session.get('user_id')
    data['slug'] = slug
    filepath = os.path.join(articles_dir, f'{slug}{articles_ext}')
    with open(filepath, encoding='utf-8', mode='w') as file:
        file.write(json.dumps(clean_data(data), ensure_ascii=False))
