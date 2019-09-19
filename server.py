import os
import re
import json
import uuid
from datetime import timedelta

from dotenv import load_dotenv
from flask import Flask, session, render_template, request, redirect, send_from_directory, url_for


MAX_SLUG_LENGTH = 100
SLUG_TRANS_MAP = {
    'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'e',
    'ж': 'zh', 'з': 'z', 'и': 'i', 'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm',
    'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u',
    'ф': 'f', 'х': 'h', 'ц': 'ts', 'ч': 'ch', 'ш': 'sh', 'щ': 'sch',
    'ъ': '', 'ы': 'y', 'ь': '', 'э': 'e', 'ю': 'y', 'я': 'ya'}
SESSION_DAYS = 90
ARTICLE_FIELDS_TO_SAVE = ['header', 'signature', 'body', 'user_id']
ERRORS = {
    'err': 'Empty header or incorrect data.',
}


app = Flask(__name__)
app.secret_key = b'fHI#56fw3h968tfbv'


def get_slug(header):
    # Get unique, user-friendly slug for url.
    slug = re.sub('[^\w ]+', '', header).strip().lower()
    slug = re.sub('[ ]+', '-', slug)
    slug = '{}_1'.format(
                    ''.join([SLUG_TRANS_MAP[a] if a in SLUG_TRANS_MAP else a for a in slug])
                    )[:MAX_SLUG_LENGTH]
    filename = f'{slug}{articles_ext}'
    while os.path.exists(os.path.join(articles_dir, filename)):
        filename_base, filename_num = filename[:-len(articles_ext)].split('_')
        slug = f'{filename_base}_{int(filename_num) + 1}'
        filename = f'{slug}{articles_ext}'
    return slug


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico',
                               mimetype='image/vnd.microsoft.icon')

def clean_data(data):
    data.fromkeys(ARTICLE_FIELDS_TO_SAVE)
    return data


@app.before_request
def auth():
    if 'user_id' not in session:
        session['user_id'] = uuid.uuid1().hex
        app.permanent_session_lifetime = timedelta(days=SESSION_DAYS)


@app.route('/', methods=['GET', 'POST'])
def index():

    if request.method == 'GET':
        return render_template('index.html')

    data = request.form.to_dict()

    # Check for empty header and valid data.
    if data['header'] == '':
        return render_template('index.html', **clean_data(data), errors=[ERRORS['err']])

    data['user_id'] = session.get("user_id")

    slug = get_slug(data['header'])

    # Write article to file and redirect.
    filepath = os.path.join(articles_dir, f'{slug}{articles_ext}')
    with open(filepath, encoding='utf-8', mode='w') as file:
        file.write(json.dumps(data, ensure_ascii=False))
    return redirect(url_for('article', slug=slug))


@app.route('/<slug>', methods=['GET', 'POST'])
def article(slug):
    filepath = os.path.join(articles_dir, f'{slug}{articles_ext}')

    # 404 handle.
    if not os.path.exists(filepath):
        return render_template('404.html')

    # Read article from file.
    with open(filepath) as file:
        data = json.loads(file.read())

    editable = data['user_id'] == session.get("user_id")

    # Not auth handle.
    if not editable and len(request.args) > 0:
        return redirect(url_for('article', slug=slug))

    # GET handle:
    # Render article page or edit page.
    if request.method == 'GET':
        mode = request.args.get('mode')
        template = 'edit.html' if mode == 'edit' else 'article.html'
        return render_template(template, **data, editable=editable)

    # POST handle:
    data = request.form.to_dict()
    data['user_id'] = session.get("user_id")

    if request.form['mode'] == 'edit':
        return render_template('edit.html', **clean_data(data), editable=editable, errors=[ERRORS['err']])

    # Save new data and redirect to article page.
    if request.form['mode'] == 'save':
        with open(filepath, encoding='utf-8', mode='w') as file:
            file.write(json.dumps(clean_data(data), ensure_ascii=False))
        return redirect(url_for('article', slug=slug))


if __name__ == "__main__":
    load_dotenv()
    host = os.environ.get('HOST')
    port = int(os.environ.get('PORT', 5500))
    articles_dir = os.environ.get('ARTICLES_DIR')
    articles_ext = os.environ.get('ARTICLES_EXT')
    app.run(host=host, port=port)
