import logging
import os
from logging.handlers import RotatingFileHandler

from flask import Flask
from flask import request
from flask_babel import Babel
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_moment import Moment
from config import Config

# osobiście nie lubie wsadzać kodu w __init__.py. Ludzie mają tendencje do olewania tego pliku i zakładania że jest pusty
# widziałbym ten kod w app.py.
# Ale to kwestia mocno preferencyjna, masz prawo zingorować tą poradę :P Ktoś inny mógłby się przyczepić, że to powinno być


app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login = LoginManager(app)
login.login_view = 'login'
babel = Babel(app)
moment = Moment(app)

if not app.debug:
    if not os.path.exists('logs'):
        os.mkdir('logs')
    file_handler = RotatingFileHandler('logs/incom.log', maxBytes=10240, backupCount=10)
    file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)

    app.logger.setLevel(logging.INFO)
    app.logger.info('InCom startup')

from app import routes, models, errors # czy to jest konieczne? Implicit import to trochę zło.import
# Importuj bezpośrednio w miejscu, w którym dkodu potrzebujesz


@babel.localeselector
def get_locale():
    return request.accept_languages.best_match(app.config['LANGUAGES'])
