import json
from os import environ as env, urandom
import re
from flask import Flask, request, abort, jsonify, render_template, redirect, url_for, session
from flask_cors import CORS
from flask_swagger import swagger
from models import setup_db, Movie, Actor, db
from urllib.parse import quote_plus, urlencode
from authlib.integrations.flask_client import OAuth
from auth import requires_auth, AuthError
from dotenv import find_dotenv, load_dotenv

ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)

# create and configure the app
app = Flask(__name__)
app.secret_key = urandom(24)
setup_db(app)
CORS(app)
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})
oauth = OAuth(app)


oauth.register(
    "auth0",
    client_id=env.get("AUTH0_CLIENT_ID"),
    client_secret=env.get("AUTH0_CLIENT_SECRET"),
    authorize_url=f'https://{env.get("AUTH0_DOMAIN")}/authorize?audience={env.get("AUTH0_AUDIENCE")}',
    server_metadata_url=f'https://{env.get("AUTH0_DOMAIN")}/.well-known/openid-configuration',
)

@app.route("/api/spec")
def spec():
    return render_template("api_doc.html", spec=swagger(app))

# Controllers API
@app.route("/")
def home():
    return render_template(
        "home.html",
        session=session.get("user"),
        pretty=json.dumps(session.get("user"), indent=4),
    )


@app.route("/callback", methods=["GET", "POST"])
def callback():
    if oauth.auth0:
        token = oauth.auth0.authorize_access_token()
        session["user"] = token
    return redirect("/")


@app.route("/login")
def login():
    if oauth.auth0:
        return oauth.auth0.authorize_redirect(
            redirect_uri=url_for("callback", _external=True)
        )
    else:
        # Handle the case when oauth.auth0 is None
        return "OAuth provider not configured."


@app.route("/logout")
def logout():
    session.clear()
    auth0_domain = env.get("AUTH0_DOMAIN") or ""
    return redirect(
        "https://"
        + auth0_domain
        + "/v2/logout?"
        + urlencode(
            {
                "returnTo": url_for("home", _external=True),
                "client_id": env.get("AUTH0_CLIENT_ID"),
            },
            quote_via=quote_plus,
        )
    )

@app.route('/actors')
@requires_auth('get:actors')
def get_actors(token):
    """
    Retrieve all actors from the database and return them as a JSON response.
    ---
    Returns:
        A JSON response containing the list of actors and a success status.
    """
    actors = Actor.query.all()
    actors = [actor.name for actor in actors]
    return jsonify({
        'success': True,
        'actors': actors
    })


@app.route('/actors', methods=['POST'])
@requires_auth('post:actors')
def create_actors(toekn):
    """
    Create a new actor.

    This function creates a new actor by extracting the name, age, and gender from the request body.
    If any of these fields are missing, a 422 error is raised.
    The new actor is then added to the database and committed.
    Finally, a JSON response is returned indicating the success of the operation and the name of the newly created actor.
    ---
    tags:  
        - Actors
    Respones:
        A JSON response containing the success status and the name of the newly created actor.
    Raises:
        422: If any of the required fields (name, age, gender) are missing.
    """
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
        abort(422)
    
@app.route('/actors/<int:actor_id>', methods=['PATCH'])
@requires_auth('patch:actors')
def update_actor(token, actor_id):
    """
    Update an actor's information.
    ---
    Args:
        actor_id (int): The ID of the actor to be updated.

    Returns:
        dict: A JSON response indicating the success of the update operation.

    Raises:
        404: If the actor with the given ID does not exist in the database.
    """
    actor = Actor.query.get(actor_id)
    if actor is None:
        abort(404)
    try:
        if 'name' in request.get_json():
            actor.name = request.get_json()['name']
        if 'age' in request.get_json():
            actor.age = request.get_json()['age']
        
        db.session.commit()
        return jsonify({
            'success': True,
            'updated': "Actor '" + str(actor.name)+"' is Updated" 
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': e
        })

@app.route('/actors/<int:actor_id>', methods=['DELETE'])
@requires_auth('delete:actors')
def delete_actor(token, actor_id):
    """
    Deletes an actor from the database.

    Parameters:
    actor_id (int): The ID of the actor to be deleted.

    Returns:
    dict: A JSON response indicating the success of the deletion and the ID of the deleted actor.
    """
    actor = Actor.query.get(actor_id)
    if actor is None:
        abort(404)
    db.session.delete(actor)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'deleted': "Actor '"+str(actor.name)+"' is Deleted"
    })

@app.route('/movies')
@requires_auth('get:movies')
def get_movies(token):
    """
    Retrieves all movies from the database.

    Returns:
        A JSON response containing the list of movies and a success flag.
    """
    movies = Movie.query.all()

    if movies is None:
        abort(404)
    return jsonify({
        'success': True,
        'movies': [movie.title for movie in movies]
    })
    
@app.route('/movies', methods=['POST'])
@requires_auth('post:movies')
def create_movies(token):
    """
    Create a new movie.

    This function creates a new movie by extracting the title and release date from the request body.
    If the title or release date is missing, it returns a 422 error.
    Otherwise, it creates a new movie object, adds it to the database, and commits the changes.
    Finally, it returns a JSON response indicating the success of the operation and the details of the created movie.

    Returns:
        A JSON response containing the success status and the details of the created movie.

    Raises:
        Exception: If an error occurs during the creation of the movie.
    """
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
            'created': "New Movie is Created with Title '" + str(new_movie.title)+"'"
        })
    
    except Exception as e:
        db.session.rollback()
        abort(422)
    
@app.route('/movies/<int:movie_id>', methods=['PATCH'])
@requires_auth('patch:movies')
def update_movie(token, movie_id):
    """
    Update a movie's title and release date.

    Args:
        movie_id (int): The ID of the movie to be updated.

    Returns:
        dict: A JSON response indicating the success of the update and the updated movie's details.
            - If the update is successful, the response will have the following format:
                {
                    'success': True,
                    'updated': "Movie [title] is Updated"
                }
            - If an error occurs during the update, the response will have the following format:
                {
                    'success': False,
                    'error': [error_message]
                }
    """
    movie = Movie.query.get(movie_id)
    if movie is None:
        abort(404)
    try:
        if 'title' in request.get_json():
            movie.title = request.get_json()['title']
        if 'release_date' in request.get_json():
            movie.release_date = request.get_json()['release_date']

        db.session.commit() 
        return jsonify({
            'success': True,
            'updated': "Movie '" + str(movie.title)+"' is Updated"
        })
    except Exception as e:
        db.session.rollback()
        abort(422)
    
@app.route('/movies/<int:movie_id>', methods=['DELETE'])
@requires_auth('delete:movies')
def delete_movie(token, movie_id):
    """
    Deletes a movie from the database.

    Args:
        movie_id (int): The ID of the movie to be deleted.

    Returns:
        dict: A JSON response indicating the success of the deletion and the ID of the deleted movie.
    """
    movie = Movie.query.get(movie_id)
    if movie is None:
        abort(404)
    
    db.session.delete(movie)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'deleted': "Movie '"+str(movie.title)+"' is Deleted"
    })

@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
    "success": False,
    "error": 422,
    "message": "unprocessable"
    }), 422


@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
        }), 404


@app.errorhandler(AuthError)
def auth_error(error):
    return jsonify({
        "success": False,
        "error": error.status_code,
        "message": error.error
    }), 401

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=env.get("PORT", 5000))

