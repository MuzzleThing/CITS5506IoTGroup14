from flask import Flask
from flask_socketio import SocketIO
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config['SECRET_KEY'] = 'amber_pearl_latte_is_the_best'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
socketio = SocketIO(app)

db = SQLAlchemy()
migrate = Migrate()

db.init_app(app)
migrate.init_app(app, db)

from app.models import Item
