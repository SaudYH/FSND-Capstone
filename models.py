import enum
import os
from sqlalchemy import Column, String, Integer, DATE, Enum
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from flask_migrate import Migrate

db = SQLAlchemy()


def setup_db(app, database_path=os.environ['DATABASE_URL']):
    app.config["SQLALCHEMY_DATABASE_URI"] = database_path
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
    migrate = Migrate(app, db)
    with app.app_context():
        db.init_app(app)
        db.create_all()

class Actor(db.Model):
    __tablename__ = 'actors'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    age = Column(Integer)
    gender = Column(Enum('Male', 'Female', name='Gender'))
    movie_id = Column(Integer, db.ForeignKey('movies.id'), nullable=True)


class Movie(db.Model):
    __tablename__ = 'movies'

    id = Column(Integer, primary_key=True)
    title = Column(String)
    release_date = Column(DATE)
    actors = relationship('Actor', backref="movie", lazy=True)

    def format(self):
        return {
            'title': self.title,
            'release_date': self.release_date,
            'actors': list(map(lambda actor: actor.name, self.actors))
        }