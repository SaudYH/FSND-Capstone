import enum
from sqlalchemy import Column, String, Integer, DATE, Enum
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

database_name = "agency"
database_path = "postgresql://{}/{}".format('localhost:5432', database_name)

db = SQLAlchemy()


def setup_db(app, database_path=database_path):
    app.config["SQLALCHEMY_DATABASE_URI"] = database_path
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
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


class Movie(db.Model):
    __tablename__ = 'Movies'

    id = Column(Integer, primary_key=True)
    title = Column(String)
    release_date = Column(DATE)

class Cast(db.Model):
    __tablename__ = 'Cast'

    id = Column(Integer, primary_key=True)
    actor_id = Column(Integer, db.ForeignKey('actors.id'))
    movie_id = Column(Integer, db.ForeignKey('Movies.id'))