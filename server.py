import os
import re
import json
from hashlib import blake2b
from hmac import compare_digest
from urllib.parse import urlsplit

from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, make_response


ARTICLES_DIR = 'articles'
ARTICLES_EXT = '.txt'
MAX_SLUG_LENGTH = 100
SLUG_CHARS = {
    'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'e',
    'ж': 'zh', 'з': 'z', 'и': 'i', 'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm',
    'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u',
    'ф': 'f', 'х': 'h', 'ц': 'ts', 'ч': 'ch', 'ш': 'sh', 'щ': 'sch',
    'ъ': '', 'ы': 'y', 'ь': '', 'э': 'e', 'ю': 'y', 'я': 'ya'}
SECRET_KEY = b'xk&$%h4788*^&'
AUTH_SIZE = 16
COOKIE_AGE = 60*60*24*30
ERRORS = {
    'empty_field': 'You must fill in all of the fields',
}

app = Flask(__name__)


def sign(cookie):
    h = blake2b(digest_size=AUTH_SIZE, key=SECRET_KEY)
    h.update(cookie.encode('utf-8'))
    return h.hexdigest()


def verify(cookie, sig):
    good_sig = sign(cookie)
    return bool(sig) and compare_digest(good_sig, sig)


def get_slug_and_filepath(header, url):
    # If article editing
    if url:
        slug = urlsplit(url).path[1:]
        return slug, os.path.join(ARTICLES_DIR, '{}{}'.format(slug, ARTICLES_EXT))
    slug = re.sub('[^\w ]+', '', header).strip().lower()
    slug = re.sub('[ ]+', '-', slug)
    slug = '{}_1'.format(
                    ''.join([SLUG_CHARS[a] if a in SLUG_CHARS else a for a in slug])
                    )[:MAX_SLUG_LENGTH]
    filename = '{}{}'.format(slug, ARTICLES_EXT)
    filepath = os.path.join(ARTICLES_DIR, filename)
    while os.path.exists(filepath):
        filename_base, filename_num = filename[:-len(ARTICLES_EXT)].split('_')
        slug = '{}_{}'.format(filename_base, int(filename_num) + 1)
        filename = '{}{}'.format(slug, ARTICLES_EXT)
        filepath = os.path.join(ARTICLES_DIR, filename)
    return slug, filepath


@app.route('/', methods=['GET', 'POST'])
def index():
    # TODO: sould implement good WYSIWYG editor
    if request.method != 'POST':
        return render_template('index.html')
    header = request.form['header']
    signature = request.form['signature']
    body = request.form['body']
    url = request.form['url']
    if header == '' or signature == '' or body == '':
        return render_template(
                    'index.html',
                    header=header,
                    signature=signature,
                    body=body,
                    error=ERRORS['empty_field'])
    slug, filepath = get_slug_and_filepath(header, url)
    with open(filepath, encoding='utf-8', mode='w') as file:
        file.write(json.dumps((header, signature, body), ensure_ascii=False))
    resp = make_response(redirect(slug, code=301))
    resp.set_cookie(slug, sign(slug), max_age=COOKIE_AGE)
    return resp


@app.route('/<slug>', methods=['GET'])
def article(slug):
    with open(os.path.join(ARTICLES_DIR, '{}.txt'.format(slug))) as file:
        header, signature, body = json.loads(file.read())
    resp = make_response(
            render_template(
                'article.html',
                 header=header,
                 signature=signature,
                 body=body,
                 url=request.base_url,
                 edit=verify(slug, request.cookies.get(slug))))
    return resp


@app.route('/edit', methods=['GET', 'POST'])
def edit():
    if request.method != 'POST':
        resp = make_response(redirect('/', code=301))
        return resp
    header = request.form['header']
    signature = request.form['signature']
    body = request.form['body']
    url = request.form['url']
    resp = make_response(
            render_template(
                'edit.html',
                **request.form))
    return resp


if __name__ == "__main__":
    load_dotenv()
    host = os.environ.get('HOST')
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
