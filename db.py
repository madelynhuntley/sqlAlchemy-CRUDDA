from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def init_db(app=None, db=None):
    db.init_app(app)