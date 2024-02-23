# Casting Agency

## Description 

A web app that manges Movies and it's cast, you can create edit and delete movies and it's actors.

## Local Installing

### Dependancees

#### Python 3.10

Follow instructions to install the latest version of python for your platform in the [python docs](https://docs.python.org/3/using/unix.html#getting-and-installing-the-latest-version-of-python)

#### Virtual Environment

We recommend working within a virtual environment whenever using Python for projects. This keeps your dependencies for each project separate and organaized. Instructions for setting up a virtual environment for your platform can be found in the [python docs](https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/)

#### PIP Dependencies

Once you have your virtual environment setup and running, install dependencies by naviging to the `/backend` directory and running:

```bash
pip install -r requirements.txt
```

This will install all of the required packages we selected within the `requirements.txt` file.

#### Key Dependencies

- [Flask](http://flask.pocoo.org/) A lightweight backend microservices framework for handling requests and responses. 

- [SQLAlchemy](https://www.sqlalchemy.org/) and [Flask-SQLAlchemy](https://flask-sqlalchemy.palletsprojects.com/en/2.x/) are libraries to handle the databse.

- [jose](https://python-jose.readthedocs.io/en/latest/) A JavaScript Object Signing and Encryption library for JWTs.

- [Auth0](https://auth0.com/docs/quickstart/webapp/python/interactive) An authentication and authorization platform for user and roles management.

- [Heroku](https://devcenter.heroku.com/categories/python-support) A cloud platform as a service (PaaS) for deploying applications.

### Databse Setup

With Postgres running, restore a database using the agency.psql file provided. From project root folder in terminal run:

```bash
psql agency < agency.sql
```

### Auth0 Setup:

To setup envirioment variables for auth0, from within the project root folder run:
```bash
source setup.sh
```
#### Optain Access tokens

To get acess tokens, you can use the login page at http://127.0.0.1:5000/login 

test users will be shared in text file (test_users.txt)

### Running the server

From within the project root directory first ensure you are working using your created virtual environment.

Each time you open a new terminal session, run:

```bash
export FLASK_APP=app.py;
```

To run the server, execute:

```bash
flask run --reload
```

The `--reload` flag will detect file changes and restart the server automatically.

### Running Tests

to run unittest we need to first obtain access tokens for all 3 roles after login with each user and coping the access toekn to the variables in test.py
```
cls.assistant_token = ""
cls.director_token = ""
cls.producer_token = ""
```
than we can run the tests from within the project root folder run:
```bash
python3 test.py
```

## API Refernce

### Getting Started 

You can import all the API's from postman collections file in prject root folder "Casting Agency.postman_collection.json"

### Error Handling 

Errors are returned as JSON objects in the following format:
```
{
    "success": False, 
    "error": 422,
    "message": "Unprocessable"
}
```

API will return 3 error types when request fails:

- 404: Resource Not Found
- 422: Unprocessable Request
- 405: Method Not Allowed
- 403: Forbidden
- 401: Authriztion error

### Endpoint 

Get /actors 

- Genral:
    - Returns list of all actors in a list of actors names.

- Sample:
    - Request: 
    ```
    curl --location 'http://127.0.0.1:5000/actors' --header 'Authorization: Bearer token
    ```

    - Response:
    ```
    {
    "actors": [
        "Robin Wright",
        "Tom Hanks",
        "Tom Hanks",
        "Robin Wright",
        "Tom Hanks",
        "Robin Wright"
    ],
    "success": true
    }
    ```

Get /movies

- Genral:
    - Return all movies and it's castin in a list of movie objects with movie title, release date and list of actors names.

- Sample:
    - Request: ```curl --location 'http://127.0.0.1:5000/movies' --header 'Authorization: Bearer token```

    - Response:
    ```
    {
    "movies": [
        {
            "actors": [
                "Tom Hanks",
                "Robin Wright"
            ],
            "release_date": "Wed, 06 Jul 1994 00:00:00 GMT",
            "title": "Forrest Gump"
        },
        {
            "actors": [
                "Tim Robbins",
                "Morgan Freeman"
            ],
            "release_date": "Fri, 23 Sep 1994 00:00:00 GMT",
            "title": "The Shawshank Redemption"
        }],
        "success": true
    }
    ```

Post /actors

- Genral:
    - Takes a dict with actor name, age, gender and movie ID.
    - Retruns success value, and messsage with new actor name.

- Sample: 
    - Request: 
    ```
    curl --location 'http://127.0.0.1:5000/actors' \
    --header 'Content-Type: application/json' \
    --header 'Authorization: Bearer token \ 
    --data '{
        "name": "Tom Hanks",
        "age": 64,
        "gender": "Male",
        "movie_id": 1
    }'
    ```

    - Response:
    ```
    {
    "created": "New Actor is Created with Name Tom Hanks",
    "success": true
    }
    ```

Post /movies

- Genral:
    - Takes a dict of movie title, release date.
    - Returns sueecces value and message with the new movie title.

- Sample:
    - Request: 
    ```
    curl --location 'http://127.0.0.1:5000/movies' \
    --header 'Content-Type: application/json' \
    --header 'Authorization: Bearer token \
    --data '{
        "title": "Forrest Gumb",
        "release_date": "1994-07-06"
    }'
    ```
    - Reponse:
    ```
    {
    "created": "New Movie is Created with Title 'Forrest Gumb'",
    "success": true
    }
    ```

Patch /actors/{actor_id}

- Genral:
    - Takes actor_id as parmater, and json with the updated variable and value.
    - Retruns success value, and messsage with updated actor name.

- Sample:
    - Request: 
    ```
    curl --location --request PATCH 'http://127.0.0.1:5000/actors/1' \
        --header 'Content-Type: application/json' \
        --header 'Authorization: Bearer token' \
        --data '{
            "age": 65
            }'
    ```
    - Response:
    ```
    {
    "success": true,
    "updated": "Actor 'Tom Hanks' is Updated"
    }
    ```

Patch /movies/{movie_id}

- Genral:
    - Takes movie_id as a parmater, and json with the updated variable and value.
    - Returns sueecces value and message with the updated movie title.

- Sample:
    - Request:
    ```
    curl --location --request PATCH 'http://127.0.0.1:5000/movies/1' \
    --header 'Content-Type: application/json' \
    --header 'Authorization: Bearer token' \
    --data '{
        "title": "Forrest Gump"
        }'
    ```
    - Resopnse:
    ```
    {
    "success": true,
    "updated": "Movie 'Forrest Gump' is Updated"
    }
    ```

Delete /actor/{actor_id}

- Genral:
    - Takes actor_id as a parameter.
    - Retruns success value, and messsage with deleted actor name.

- Sample:
    - Request:
    ```
    curl --location --request DELETE 'http://127.0.0.1:5000/actors/1' --header 'Authorization: Bearer token'
    ```
    - Response:
    ```
    {
    "deleted": "Actor 'Tom Hanks' is Deleted",
    "success": true
    }
    ```

Delete /movies/{movie_id}

- Genral:
    - Takes movie_id as a parameter.
    - Returns sueecces value and message with the deleted movie title.

- Sample:
    - Request: 
    ```
    curl --location --request DELETE 'http://127.0.0.1:5000/movies/1' --header 'Authorization: Bearer token'
    ```
    - Response:
    ```
    {
    "deleted": "Movie 'Forrest Gump' is Deleted",
    "success": true
    }
    ```

## Cloud Hosting 

The Casting Agency application is deployed to Heroku, accessible at [Heroku Application URL]. Login credentials are shared in the user_cred.txt file. Copy the access tokens to use the API with Postman, utilizing the provided Postman collection.