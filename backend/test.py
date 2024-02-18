import code
import unittest
import json
from flask import app
import requests
from models import db
from app import app
from dotenv import find_dotenv, load_dotenv
from os import access, environ as env
from unittest.mock import patch

ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)

def get_auth0_token():
    domain = env.get("TEST_AUTH0_DOMAIN")
    client_id = env.get("TEST_AUTH0_CLIENT_ID")
    client_secret = env.get("TEST_AUTH0_CLIENT_SECRET")
    audience = env.get("TEST_AUTH0_AUDIENCE")
    url = f"https://{domain}/oauth/token"
    headers = {"content-type": "application/json"}
    payload = {
        "client_id": client_id,
        "client_secret": client_secret,
        "audience": audience,
        "grant_type": "client_credentials"
    }
    
    for role in ["assistant", "director", "producer"]:
        if role == "assistant":
            payload["scope"] = "get:actors get:movies"
            response = requests.post(url, data=json.dumps(payload), headers=headers)
            assistant_token = response.json()["access_token"]
        elif role == "director":
            payload["scope"] = "get:actors get:movies post:actors patch:actors patch:movies delete:actors"
            response = requests.post(url, data=json.dumps(payload), headers=headers)
            director_token = response.json()["access_token"]
        else:
            payload["scope"] = "get:actors get:movies post:actors post:movies patch:actors patch:movies delete:actors delete:movies"
            response = requests.post(url, data=json.dumps(payload), headers=headers)
            producer_token = response.json()["access_token"]

    return assistant_token, director_token, producer_token

class CastingAgencyTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        super(CastingAgencyTestCase, cls).setUpClass()
        cls.assistant_token = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IlNQVWVPOWJTNHFVZWRTUGlCYUgyWiJ9.eyJpc3MiOiJodHRwczovL2Rldi1sY2Ria2Uyemc1MXUxZXV0LnVzLmF1dGgwLmNvbS8iLCJzdWIiOiJhdXRoMHw2NWNiMTlmNjIwMTNiY2I4ZDJmZjA4YmYiLCJhdWQiOiJodHRwOi8vMTI3LjAuMC4xOjUwMDAvYWN0b3JzIiwiaWF0IjoxNzA4MTc1MTQxLCJleHAiOjE3MDgyNjE1NDEsImF6cCI6ImFSMGo4S0p2M0swOFl6NU1ka2VzWG1BbGFYaWl6UEZUIiwicGVybWlzc2lvbnMiOlsiZ2V0OmFjdG9ycyIsImdldDptb3ZpZXMiXX0.FjdIh9MyYS1rJYjKRYo7qs5b4i9yNw_3FxcInGTnwVfL1eRDK5A4csei1MY_g6isdbTRhmCyIrwPu4q120yO0hpCmaxoTviyVosUDJOPNhK72-wB-CL9NS238iNRc1b7oXXt9g0xodPhhMLJjdnlNTRhhx2IJnXE0IOaB_b29VQg4EBjermKc0xMsMMIc0vSplwC5gISWveUY1TMHRfofxGXc-4CW48Z7eIJoPGyxDsDZw2pk2kGdNqbvvnFOp_wrE9PsBNKAu48fAJW6IImrOZJGiwE50I4hdsSAovFV6eb44E8v0Hy31Ahy1nbLLynsLkhNwjmSsIKzuS_V75Isw"
        cls.director_token = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IlNQVWVPOWJTNHFVZWRTUGlCYUgyWiJ9.eyJpc3MiOiJodHRwczovL2Rldi1sY2Ria2Uyemc1MXUxZXV0LnVzLmF1dGgwLmNvbS8iLCJzdWIiOiJhdXRoMHw2NWNiMWEzOTA0ZjY2ZGM2OGUxZDNkNzgiLCJhdWQiOiJodHRwOi8vMTI3LjAuMC4xOjUwMDAvYWN0b3JzIiwiaWF0IjoxNzA4MTc1MjQwLCJleHAiOjE3MDgyNjE2NDAsImF6cCI6ImFSMGo4S0p2M0swOFl6NU1ka2VzWG1BbGFYaWl6UEZUIiwicGVybWlzc2lvbnMiOlsiZGVsZXRlOmFjdG9ycyIsImdldDphY3RvcnMiLCJnZXQ6bW92aWVzIiwicGF0Y2g6YWN0b3JzIiwicGF0Y2g6bW92aWVzIiwicG9zdDphY3RvcnMiXX0.L6WYXdKwFnrO13KkVYtzVyjMTY8BSdyED9EK9Hd-9Oj6Swfesw7iiobZdAp50vXNTttkcCNO52v-1vgzDtAEePSUpsI8s9QV6p7ydJR3SDVMFhvHsIOE8cfCTWGMBf6pdISatEEdjBkSxsZ-1miJH1aMIuiSJL3aIlytEc0ULbJnJA6awEO17snVx_5n_0HWOsMI5sNlykRcN0_I5E5SkQWk3CL8WRqrERXmgQEXSJRukzzDgkk4-lJDKkyVedcGyeBvqqpRKfksXuCDhoYxsGgCconuHu98j5ftrtu3WtSjobcBkZzYhnndT1vRCYO_yyszPdFW5iEfb1ILHIMu2w"
        cls.producer_token = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IlNQVWVPOWJTNHFVZWRTUGlCYUgyWiJ9.eyJpc3MiOiJodHRwczovL2Rldi1sY2Ria2Uyemc1MXUxZXV0LnVzLmF1dGgwLmNvbS8iLCJzdWIiOiJhdXRoMHw2NWNiMWE3NTg4YzljMjYyMzJlYmFiYTMiLCJhdWQiOiJodHRwOi8vMTI3LjAuMC4xOjUwMDAvYWN0b3JzIiwiaWF0IjoxNzA4MTc1MzQ0LCJleHAiOjE3MDgyNjE3NDQsImF6cCI6ImFSMGo4S0p2M0swOFl6NU1ka2VzWG1BbGFYaWl6UEZUIiwicGVybWlzc2lvbnMiOlsiZGVsZXRlOmFjdG9ycyIsImRlbGV0ZTptb3ZpZXMiLCJnZXQ6YWN0b3JzIiwiZ2V0Om1vdmllcyIsInBhdGNoOmFjdG9ycyIsInBhdGNoOm1vdmllcyIsInBvc3Q6YWN0b3JzIiwicG9zdDptb3ZpZXMiXX0.cL_ik5l0BqE7qOEPp9f6Y2soQvMQljATq_D6cWSgx0SpNqyWR9_0pY8j3It0Zo9eLAkFyYooCu9ADdlfuKVZ97FkEpFJZslid0v8HTr_Kl4sPoziuTKU3wXd2FJC1iVXgJjfbedR8b3vbGd640qACse4JrsuMrRdxOyGK49sRmQbE1HCdz6pK0YNvHECD1YqBW6w_V0D70cqdV_RaSKqZaaIpIZcYKB54sAyQoPq35DF3mSuMTRRzG-QopTtVIXrMefyLhiZPivT7UqeImAI6TDluJUFxkdEJUOE0Nch_jO3IXuPzcutG7X4c0xZlL13vTaaXgofnrAlifbqXLX95w"

    @classmethod
    def tearDownClass(cls):
        try:
            with app.app_context():
                db.drop_all()
                db.session.commit()
        except Exception as e:
            print(f"Error during tearDownClass: {e}")
        super(CastingAgencyTestCase, cls).tearDownClass()

    def setUp(self):
        self.database_name = "agency_test"
        self.database_path = "postgres://{}/{}".format('localhost:5432', self.database_name)
        app.config["SQLALCHEMY_DATABASE_URI"] = self.database_path
        self.client = app.test_client()

        self.patcher = patch('test.get_auth0_token')
        self.mock_get_auth0_token = self.patcher.start()
        self.mock_get_auth0_token.return_value = (self.assistant_token, self.director_token, self.producer_token)
        
        app.app_context().push()
        
        # setup_db(self.app, self.database_path)

        self.new_actor = {
            "name": "Tom Hanks",
            "age": 64,
            "gender": 'Male'        
        }

        self.new_actor_2 = {
            "name": "Robin Wright",
            "age": 54,
            "gender": "Male"
        }

        self.new_movie = {
            "title": "Forrest Gumb",
            "release_date": "1994-07-06"
        }

        self.new_movie_2 = {
            "title": "The Shawshank Redemption",
            "release_date": "1994-09-23"
        }
        
        with app.app_context():
            # self.db = SQLAlchemy()
            # self.db.init_app(self.app)
            db.create_all()
    
    def tearDown(self):
        db.session.remove()
        db.session.rollback()
        
        
    def test_create_actor(self):
        headers = {"Authorization": f"Bearer {self.director_token}",
                   "Content-Type": "application/json"}
        res = self.client.post('/actors', json=self.new_actor, headers=headers)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['created'])

    def test_create_movie(self):
        headers = {"Authorization": f"Bearer {self.producer_token}",
                   "Content-Type": "application/json"}    
        res = self.client.post('/movies', json=self.new_movie, headers=headers)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['created'])

    def test_create_actor2(self):
        headers = {"Authorization": f"Bearer {self.director_token}",
                   "Content-Type": "application/json"}
        res = self.client.post('/actors', json=self.new_actor_2, headers=headers)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['created'])

    def test_create_movie2(self):
        headers = {"Authorization": f"Bearer {self.producer_token}"}    
        res = self.client.post('/movies', json=self.new_movie_2, headers=headers)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['created'])

    def test_get_actors(self):
        headers = {"Authorization": f"Bearer {self.assistant_token}"}
        res = self.client.get('/actors', headers=headers)
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['actors'])

    def test_get_movies(self):
        headers = {"Authorization": f"Bearer {self.assistant_token}"}
        res = self.client.get('/movies', headers=headers)
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['movies'])

    def test_update_actor(self):
        headers = {"Authorization": f"Bearer {self.director_token}"}
        res = self.client.patch('/actors/1', json={"age": 65}, headers=headers)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['updated'])

    def test_update_movie(self):
        headers = {"Authorization": f"Bearer {self.producer_token}"}
        res = self.client.patch('/movies/1', json={"title": "Forrest Gump"}, headers=headers)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['updated'])

    def test_delete_actor(self):
        headers = {"Authorization": f"Bearer {self.producer_token}"}
        res = self.client.delete('/actors/2', headers=headers)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['deleted'])

    def test_delete_movie(self):
        headers = {"Authorization": f"Bearer {self.producer_token}"}
        res = self.client.delete('/movies/2', headers=headers)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['deleted'])

    def test_422_if_actor_creation_fails(self):
        headers = {"Authorization": f"Bearer {self.director_token}"}
        res = self.client.post('/actors', json={}, headers=headers)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], "unprocessable")
    
    def test_422_if_movie_creation_fails(self):
        headers = {"Authorization": f"Bearer {self.producer_token}"}
        res = self.client.post('/movies', json={}, headers=headers)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], "unprocessable")

    def test_401_if_actor_deletion_fails(self):
        headers = {"Authorization": f"Bearer {self.assistant_token}"}
        res = self.client.delete('/actors/1', headers=headers)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 401)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message']['code'], "unauthorized")

    def test_401_if_movie_deletion_fails(self):
        headers = {"Authorization": f"Bearer {self.director_token}"}
        res = self.client.delete('/movies/1', headers=headers)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 401)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message']['code'], "unauthorized")

    def test_401_if_actor_creation_fails(self):
        headers = {"Authorization": f"Bearer {self.assistant_token}"}
        res = self.client.delete('/actors/1', headers=headers)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 401)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message']['code'], "unauthorized")

    def test_401_if_movie_creation_fails(self):
        headers = {"Authorization": f"Bearer {self.director_token}"}
        res = self.client.delete('/movies/1', headers=headers)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 401)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message']['code'], "unauthorized")

    def test_401_if_actor_update_fails(self):
        headers = {"Authorization": f"Bearer {self.assistant_token}"}
        res = self.client.delete('/actors/1', headers=headers)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 401)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message']['code'], "unauthorized")

    def test_401_if_movie_update_fails(self):
        headers = {"Authorization": f"Bearer {self.assistant_token}"}
        res = self.client.delete('/movies/1', headers=headers)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 401)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message']['code'], "unauthorized")
    
if __name__ == "__main__":
    unittest.main()
        

