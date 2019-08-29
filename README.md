# Telegraph Clone

[This site](https://my-telegraph.herokuapp.com/) is a simple service for publish anonymous articles, like telegra.ph. Any user can creates an article and gets unique user-friendly url for it. User can edits articles without login and password (authorization works with cookies). Every article stores in txt-file.


# How to Install

Python 3.6 and libraries from **requirements.txt** should be installed.

```bash

$ pip install -r requirements.txt
```

Put all necessary parameters to .env file.

```bash
FLASK_DEBUG=TRUE
PORT=8000
HOST=0.0.0.0
ARTICLES_DIR=articles_dir_name
ARTICLES_EXT=.txt
```

FLASK_DEBUG environment variable Flask loads by itself, but for PORT loading we should use python-dotenv package.


# Quickstart

1. Run **server.py**.

```bash

$ python server.py

 * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
 * Restarting with inotify reloader
 * Debugger is active!

```

2. Goto [http://127.0.0.1:8000/ ](http://127.0.0.1:8000/ )


# How to Deploy

For example, you can deploy the site on [Heroku](https://heroku.com), with
GitHub integration.

1. Create a new app on Heroku with GitHub deployment method.

2. Do not forget about **Procfile**:

```bash

web: python3 server.py

```

3. Add your environment variables to Settings > Config Vars section (FLASK_DEBUG and PORT). Use PORT=80

4. Open https://[your-app-name].herokuapp.com/ in your browser

5. For reading logs install [Heroku CLI](https://devcenter.heroku.com/articles/heroku-cli#download-and-install), log in and use:

```bash
$ heroku logs -t --app app-name
```


# Project Goals

The code is written for educational purposes. Training course for web-developers - [DEVMAN.org](https://devman.org)
