import os
from flask import Flask, request, abort, jsonify
from flask_cors import CORS
from models import setup_db, Movie, Actor, db


def create_app(test_config=None):
    app = Flask(__name__)

    setup_db(app)
    CORS(app)
    # a simple page that says hello

    @app.route('/actors')
    def get_actors():
        actors = Actor.query.all()
        return jsonify({
            'success': True,
            'actors': [actor.format() for actor in actors]
        })

    
    @app.route('/actors', methods=['POST'])
    def create_actors():
        try:
            body = request.get_json()

            name = body.get('name', None)
            age = body.get('age', None)
            gender = body.get('gender', None)

            if name is None or age is None or gender is None:
                abort(422)

            new_actor = Actor()
            new_actor.name = name
            new_actor.age = age
            new_actor.gender = gender

            db.session.add(new_actor) 
            db.session.commit()  

            return jsonify({
                'success': True,
                'created': "New Actor is Created with Name " + str(new_actor.name)
            })
        
        except Exception as e:
            db.session.rollback()
            return jsonify({
                'success': False,
                'error': e
            })
        
    @app.route('/actors/<int:actor_id>', methods=['PATCH'])
    def update_actor(actor_id):
        actor = Actor.query.get(actor_id)
        if actor is None:
            abort(404)
        try:
            actor.name = request.get_json()['name']
            actor.age = request.get_json()['age']
            db.session.commit()
            return jsonify({
                'success': True,
                'updated': "Actor " + str(actor.title)+" is Updated" 
            })
        except Exception as e:
            db.session.rollback()
            return jsonify({
                'success': False,
                'error': e
            })
    
    @app.route('/actors/<int:actor_id>', methods=['DELETE'])
    def delete_actor(actor_id):
        actor = Actor.query.get(actor_id)
        if actor is None:
            abort(404)
        actor.delete()
        return jsonify({
            'success': True,
            'deleted': actor_id
        })
    
    @app.route('/movies')
    def get_movies():
        movies = Movie.query.all()
        return jsonify({
            'success': True,
            'movies': [movie.format() for movie in movies]
        })
        
    @app.route('/movies', methods=['POST'])
    def create_movies():
        try:
            body = request.get_json()

            title = body.get('title', None)
            release_date = body.get('release_date', None)

            if title is None or release_date is None:
                abort(422)
            
            new_movie = Movie()
            new_movie.title=title
            new_movie.release_date=release_date
            
            db.session.add(new_movie)
            db.session.commit()

            return jsonify({
                'success': True,
                'created': "New Movie is Created with Title " + str(new_movie.title)
            })
        
        except Exception as e:
            db.session.rollback()
            return jsonify({
                'success': False,
                'error': e
            })
        
    @app.route('/movies/<int:movie_id>', methods=['PATCH'])
    def update_movie(movie_id):
        movie = Movie.query.get(movie_id)
        if movie is None:
            abort(404)
        try:
            movie.title = request.get_json()['title']
            movie.release_date = request.get_json()['release_date']
            db.session.commit() 
            return jsonify({
                'success': True,
                'updated': "Movie " + str(movie.title)+" is Updated"
            })
        except Exception as e:
            db.session.rollback()
            return jsonify({
                'success': False,
                'error': str(e)
            })
        
    @app.route('/movies/<int:movie_id>', methods=['DELETE'])
    def delete_movie(movie_id):
        movie = Movie.query.get(movie_id)
        if movie is None:
            abort(404)
        movie.delete()
        return jsonify({
            'success': True,
            'deleted': movie_id
        })

    return app
