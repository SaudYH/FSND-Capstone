import unittest
import json
import requests
from models import db
from app import create_app
from dotenv import find_dotenv, load_dotenv

ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)

def get_auth0_token(domain, client_id, client_secret, audience, scope=""):
    url = f"https://{domain}/oauth/token"
    headers = {"content-type": "application/json"}
    payload = {
        "client_id": client_id,
        "client_secret": client_secret,
        "audience": audience,
        "grant_type": "client_credentials",
        "scope": scope
    }
    
    response = requests.post(url, json=payload, headers=headers)
    response_data = response.json()
    
    if response.status_code == 200:
        return response_data["access_token"]
    else:
        raise Exception("Failed to obtain token: " + response_data.get("error_description", "No error description provided"))

class CastingAgencyTestCase(unittest.TestCase):
    DOMAIN = env.get("AUTH0_DOMAIN")
    CLIENT_ID = env.get("AUTH0_CLIENT_ID")
    CLIENT_SECRET = "YOUR_CLIENT_SECRET"
    AUDIENCE = "YOUR_API_AUDIENCE"

    def setUp(self):
        self.database_name = "agency_test"
        self.database_path = "postgres://{}/{}".format('localhost:5432', self.database_name)
        self.app = create_app({"SQLALCHEMY_DATABASE_URI": self.database_path, "SQLALCHEMY_TRACK_MODIFICATIONS": False})
        self.client = self.app.test_client
        self.assistnt_token = get_auth0_token(self.DOMAIN, self.CLIENT_ID, self.CLIENT_SECRET, self.AUDIENCE, "get:actors get:movies")
        self.director_token = get_auth0_token(self.DOMAIN, self.CLIENT_ID, self.CLIENT_SECRET, self.AUDIENCE, "get:actors get:movies post:actors patch:actors patch:movies delete:actors")
        self.producer_token = get_auth0_token(self.DOMAIN, self.CLIENT_ID, self.CLIENT_SECRET, self.AUDIENCE, "get:actors get:movies post:actors post:movies patch:actors patch:movies delete:actors delete:movies")
        
        # setup_db(self.app, self.database_path)

        self.new_actor = {
            "name": "Tom Hanks",
            "age": 64,
            "gender": 'Male'        
        }
        self.new_movie = {
            "title": "Forrest Gumb",
            "release_date": "1994-07-06"
        }
        
        with self.app.app_context():
            # self.db = SQLAlchemy()
            # self.db.init_app(self.app)
            db.create_all()
    
    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_get_actors(self):
        res = self.client().get('/actors')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], 200)
        self.assertTrue(data['actors'])

    def test_get_movies(self):
        res = self.client().get('/movies')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], 200)
        self.assertTrue(data['movies'])

    def test_create_actor(self):
        res = self.client().post('/actors', json=self.new_actor)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], 200)
        self.assertTrue(data['actor'])

    def test_create_movie(self):
        res = self.client().post('/movies', json=self.new_movie)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], 200)
        self.assertTrue(data['movie'])

    def test_update_actor(self):
        res = self.client().patch('/actors/1', json={"age": 65})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], 200)
        self.assertTrue(data['actor'])

    def test_update_movie(self):
        res = self.client().patch('/movies/1', json={"title": "Forrest Gump"})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], 200)
        self.assertTrue(data['movie'])

    def test_delete_actor(self):
        res = self.client().delete('/actors/1')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], 200)
        self.assertEqual(data['delete'], 1)

    def test_delete_movie(self):
        res = self.client().delete('/movies/1')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], 200)
        self.assertEqual(data['delete'], 1)

    def test_404_if_actors_not_found(self):
        res = self.client().get('/actors/1000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], 404)
        self.assertEqual(data['message'], "Resource Not Found")

    def test_404_if_movies_not_found(self):
        res = self.client().get('/movies/1000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], 404)
        self.assertEqual(data['message'], "Resource Not Found")

    def test_400_if_actor_creation_fails(self):
        res = self.client().post('/actors', json={})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['success'], 400)
        self.assertEqual(data['message'], "Bad Request")
    
    def test_400_if_movie_creation_fails(self):
        res = self.client().post('/movies', json={})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['success'], 400)
        self.assertEqual(data['message'], "Bad Request")

    def test_401_if_actor_deletion_fails(self):
        res = self.client().delete('/actors/1')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 401)
        self.assertEqual(data['success'], 401)
        self.assertEqual(data['message'], "Unauthorized")

    
if __name__ == "__main__":
    unittest.main()
        

