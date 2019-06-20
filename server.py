import os
import re
import json
import uuid

from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, make_response, send_from_directory


MAX_SLUG_LENGTH = 100
SLUG_TRANS_MAP = {
    'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'e',
    'ж': 'zh', 'з': 'z', 'и': 'i', 'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm',
    'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u',
    'ф': 'f', 'х': 'h', 'ц': 'ts', 'ч': 'ch', 'ш': 'sh', 'щ': 'sch',
    'ъ': '', 'ы': 'y', 'ь': '', 'э': 'e', 'ю': 'y', 'я': 'ya'}
COOKIE_AGE = 60*60*24*30
ERRORS = {
    'empty_header': 'You must fill in header at least.',
}

app = Flask(__name__)


def get_slug(header):
    # Get unique, user-friendly slug for url.
    slug = re.sub('[^\w ]+', '', header).strip().lower()
    slug = re.sub('[ ]+', '-', slug)
    slug = '{}_1'.format(
                    ''.join([SLUG_TRANS_MAP[a] if a in SLUG_TRANS_MAP else a for a in slug])
                    )[:MAX_SLUG_LENGTH]
    filename = '{}{}'.format(slug, articles_ext)
    while os.path.exists(os.path.join(articles_dir, filename)):
        filename_base, filename_num = filename[:-len(articles_ext)].split('_')
        slug = '{}_{}'.format(filename_base, int(filename_num) + 1)
        filename = '{}{}'.format(slug, articles_ext)
    return slug


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico',
                               mimetype='image/vnd.microsoft.icon')


@app.route('/', methods=['GET', 'POST'])
def index():
    # TODO: implementation WYSIWYG editor and JS fields checking.
    if request.method == 'GET':
        return render_template('index.html')
    data = request.form.to_dict()

    # Check for empty header.
    # TODO: implementation JS fields checking.
    if data['header'] == '':
        return render_template(
                    'index.html',
                    **data,
                    errors=[ERRORS['empty_header']])

    slug = get_slug(data['header'])
    resp = make_response(redirect(slug, code=301))

    # Cookie auth process.
    user_id = request.cookies.get('user_id')
    if user_id is None:
        user_id = str(uuid.uuid1())
        resp.set_cookie('user_id', user_id, max_age=COOKIE_AGE)
    data['user_id'] = user_id

    # Write article to file.
    filepath = os.path.join(articles_dir, '{}{}'.format(slug, articles_ext))
    with open(filepath, encoding='utf-8', mode='w') as file:
        file.write(json.dumps(data, ensure_ascii=False))

    return resp


@app.route('/<slug>', methods=['GET', 'POST'])
def article(slug):

    # Read article from file.
    filepath = os.path.join(articles_dir, '{}{}'.format(slug, articles_ext))
    with open(filepath) as file:
        data = json.loads(file.read())

    # Cookie auth process.
    user_id = request.cookies.get('user_id')
    editable = data['user_id'] == user_id

    # Url handle logic.
    if request.method == 'GET':
        resp = make_response(render_template(
                                'article.html',
                                **data,
                                editable=editable))

    elif request.form['process'] == 'edit':
        resp = make_response(render_template(
                                'edit.html',
                                **data))

    elif request.form['process'] == 'save':
        data = request.form.to_dict()
        del(data['process'])
        data['user_id'] = user_id
        with open(filepath, encoding='utf-8', mode='w') as file:
            file.write(json.dumps(data, ensure_ascii=False))
        resp = make_response(render_template(
                                'article.html',
                                **data,
                                editable=editable))

    return resp


if __name__ == "__main__":
    load_dotenv()
    host = os.environ.get('HOST')
    port = int(os.environ.get('PORT', 5000))
    articles_dir = os.environ.get('ARTICLES_DIR')
    articles_ext = os.environ.get('ARTICLES_EXT')
    app.run(host=host, port=port)
