import os
import uuid
from datetime import timedelta

from dotenv import load_dotenv
from flask import (Flask, session, render_template, request, redirect, 
                    send_from_directory, url_for, abort)

from article_tools import get_slug, clean_data, read_article, write_article

SESSION_DAYS = 90
ERRORS = {
    'err': 'Empty header or incorrect data.',
}


app = Flask(__name__)
app.secret_key = b'fHI#56fw3h968tfbv'


@app.before_request
def auth():
    if 'user_id' not in session:
        session['user_id'] = uuid.uuid1().hex
        app.permanent_session_lifetime = timedelta(days=SESSION_DAYS)


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico',
                               mimetype='image/vnd.microsoft.icon')


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        return render_template('index.html')
    form_data = request.form.to_dict()
    if form_data['header'] == '':
        return render_template('index.html', **clean_data(form_data), errors=[ERRORS['err']])
    slug = get_slug(form_data['header'])
    write_article(slug, form_data, session)
    return redirect(url_for('article', slug=slug))


@app.route('/<slug>', methods=['GET'])
def article(slug):
    file_data = read_article(slug)
    editable = file_data['user_id'] == session.get('user_id')
    return render_template('article.html', **file_data, editable=editable)


@app.route('/<slug>/edit', methods=['POST', 'GET'])
def edit_article(slug):
    if request.form.get('edit'):
        file_data = read_article(slug)
        return render_template('edit.html', **clean_data(file_data))
    form_data = request.form.to_dict()
    write_article(slug, form_data, session)
    if request.form.get('save'):
        return render_template('edit.html', **clean_data(form_data))
    elif request.form.get('publish'):
        return redirect(url_for('article', slug=slug))
    else:
        abort(403)


if __name__ == "__main__":
    load_dotenv()
    host = os.environ.get('HOST')
    port = int(os.environ.get('PORT', 5500))
    app.run(host=host, port=port)
