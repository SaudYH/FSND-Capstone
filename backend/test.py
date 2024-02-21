import unittest
import json
import requests
from models import setup_db
from app import create_app, db
from dotenv import find_dotenv, load_dotenv
from os import environ as env
from unittest.mock import patch
from sqlalchemy import text

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
        cls.app = create_app(test_config=True)
        cls.client = cls.app.test_client()
        cls.app_context = cls.app.app_context()
        cls.app_context.push()  # Activate app context for setup
        cls.database_name = "agency_test"
        cls.database_path = "postgresql://{}/{}".format('localhost:5432', cls.database_name)
        setup_db(cls.app, cls.database_path)
        db.create_all()  # Create all tables
        try:
            with db.engine.connect() as connection:
                connection.execute(text("ALTER SEQUENCE actors_id_seq RESTART WITH 1;"))
                connection.execute(text("ALTER SEQUENCE movies_id_seq RESTART WITH 1;"))
        except Exception as e:
            print(f"Error resetting sequences: {e}")
        cls.assistant_token = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IlNQVWVPOWJTNHFVZWRTUGlCYUgyWiJ9.eyJpc3MiOiJodHRwczovL2Rldi1sY2Ria2Uyemc1MXUxZXV0LnVzLmF1dGgwLmNvbS8iLCJzdWIiOiJhdXRoMHw2NWNiMTlmNjIwMTNiY2I4ZDJmZjA4YmYiLCJhdWQiOiJodHRwOi8vMTI3LjAuMC4xOjUwMDAvYWN0b3JzIiwiaWF0IjoxNzA4NTA1OTM4LCJleHAiOjE3MDg1OTIzMzgsImF6cCI6ImFSMGo4S0p2M0swOFl6NU1ka2VzWG1BbGFYaWl6UEZUIiwicGVybWlzc2lvbnMiOlsiZ2V0OmFjdG9ycyIsImdldDptb3ZpZXMiXX0.dcQjZxVjvECiZSyvc2ECF0a0UEy0jJdkPIQ9UEah5irV3PTWC3Wxsvc0pBPvLwN4ACYCvH-g_7wLkj4JJl1pJhl9KleFhkL0HcUKKhnHXm3ZHqJfigujYJeSvoYMRAqWwhWyqGjc2vOtWZIfsqWpSxLVPlhmZT-MP9kOKh4THOYoDigYn0MvG8GV3XhslelHIxBgFWP21q-DVLUYi_gZDQaIbaZOT3Jc92p_-BdwDA9uzAdpdS0saRXMhsMRzz52AI93DWedrh_5Cg2z4l1VD07t6b_uv_LuTzJqQPZGGlwn7781M8LEAZW69kkMXR_j7aRnnhLB4Pq7T1XVZxBKgg"
        cls.director_token = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IlNQVWVPOWJTNHFVZWRTUGlCYUgyWiJ9.eyJpc3MiOiJodHRwczovL2Rldi1sY2Ria2Uyemc1MXUxZXV0LnVzLmF1dGgwLmNvbS8iLCJzdWIiOiJhdXRoMHw2NWNiMWEzOTA0ZjY2ZGM2OGUxZDNkNzgiLCJhdWQiOiJodHRwOi8vMTI3LjAuMC4xOjUwMDAvYWN0b3JzIiwiaWF0IjoxNzA4NTA1OTAyLCJleHAiOjE3MDg1OTIzMDIsImF6cCI6ImFSMGo4S0p2M0swOFl6NU1ka2VzWG1BbGFYaWl6UEZUIiwicGVybWlzc2lvbnMiOlsiZGVsZXRlOmFjdG9ycyIsImdldDphY3RvcnMiLCJnZXQ6bW92aWVzIiwicGF0Y2g6YWN0b3JzIiwicGF0Y2g6bW92aWVzIiwicG9zdDphY3RvcnMiXX0.Q-IPAGZsy7U-cbGco4Csee2jvLU94wWnycKJ35-V2uQvSUvtxQAcqVbFc9YAE501TyfZep1bAi1Xk0bBqdl3gDa8JFkG1RuVKn2hFRYjunkbFa8rxmyY-7bBAMNDTwttbdKbzQfa6RLzG0UJBoiulmsz3HbXrGa7sL9xFaokZyRZ5-10BdWJ3egq2x5GslKLGCNVkChyx0GQsz-43KnOfQ0IcpW6KsgCGNWgO7x2E_lN2CSXpZbnUAXSO5QvW1XP1IOuhLvY9ZB1Hm1kbNRNLYP3nwyAXPL7cW2xkeILekLhZs86u0dKcsNTOWAAx0pa2yIQlK5ZcuS1havJTb1JJg"
        cls.producer_token = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IlNQVWVPOWJTNHFVZWRTUGlCYUgyWiJ9.eyJpc3MiOiJodHRwczovL2Rldi1sY2Ria2Uyemc1MXUxZXV0LnVzLmF1dGgwLmNvbS8iLCJzdWIiOiJhdXRoMHw2NWNiMWE3NTg4YzljMjYyMzJlYmFiYTMiLCJhdWQiOiJodHRwOi8vMTI3LjAuMC4xOjUwMDAvYWN0b3JzIiwiaWF0IjoxNzA4NTAzMDQ5LCJleHAiOjE3MDg1ODk0NDksImF6cCI6ImFSMGo4S0p2M0swOFl6NU1ka2VzWG1BbGFYaWl6UEZUIiwicGVybWlzc2lvbnMiOlsiZGVsZXRlOmFjdG9ycyIsImRlbGV0ZTptb3ZpZXMiLCJnZXQ6YWN0b3JzIiwiZ2V0Om1vdmllcyIsInBhdGNoOmFjdG9ycyIsInBhdGNoOm1vdmllcyIsInBvc3Q6YWN0b3JzIiwicG9zdDptb3ZpZXMiXX0.RiOSOttliQyH_KOFaN7HUC6unDCIAbQltdf0_-Ps6cHvmS45viYW_Mo2UuFA0mZU-hlg7hBJNUnnRuzo3wDtwe79Fn8X9DGIA2EGajdfPDwaG_Gj-7r4M6w7XJblrPt8_PBvjCahqcA6gybSOmrJfaOJC0VqKegDAaeoTVqtc_IOB88ki626aHULSXludwfHBoUP_TtFeOoDoKpPxNwt_8VE9N-r6J0Yku_tVeE2JtaerPRXRhewT5yuv10yYfC-SHqKQU8iJwdrm1tZwEUHpUAkKkJNypkMr6ZryC_Bh0pR2WL31fcInDusQKwB-lm6DW3kaOm9HBgw-w_OWNWjnQ"

    @classmethod
    def tearDownClass(cls):
        cls.app_context.push()  # Ensure app context is pushed for teardown
        db.session.remove()
        db.drop_all()  # Drop all tables
        cls.app_context.pop()  # Pop app context
        super(CastingAgencyTestCase, cls).tearDownClass()

    def setUp(self):
        self.patcher = patch('test.get_auth0_token')
        self.mock_get_auth0_token = self.patcher.start()
        self.mock_get_auth0_token.return_value = (
            self.assistant_token, self.director_token, self.producer_token
        )

        self.new_actor = {
            "name": "Tom Hanks",
            "age": 64,
            "gender": 'Male',
            "movie_id": 1
        }

        self.new_actor_2 = {
            "name": "Tim Robbins",
            "age": 62,
            "gender": 'Male',
            "movie_id": 2
        }

        self.new_actor_3 = {
            "name": "Robin Wright",
            "age": 54,
            "gender": "Female",
            "movie_id": 1
        }

        self.new_actor_4 = {
            "name": "Morgan Freeman",
            "age": 70,
            "gender": 'Male',
            "movie_id": 2
        }

        self.new_movie = {
            "title": "Forrest Gumb",
            "release_date": "1994-07-06",
        }

        self.new_movie_2 = {
            "title": "The Shawshank Redemption",
            "release_date": "1994-09-23",
        }

    # def tearDown(self):
    #     self.patcher.stop()
    #     db.session.rollback()
        

    def test_01_create_movie(self):
        headers = {"Authorization": f"Bearer {self.producer_token}",
                   "Content-Type": "application/json"}    
        res = self.client.post('/movies', json=self.new_movie, headers=headers)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['created'])

    def test_02_create_movie2(self):
        headers = {"Authorization": f"Bearer {self.producer_token}"}    
        res = self.client.post('/movies', json=self.new_movie_2, headers=headers)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['created'])
    
    def test_03_create_actor(self):
        headers = {"Authorization": f"Bearer {self.director_token}",
                   "Content-Type": "application/json"}
        res = self.client.post('/actors', json=self.new_actor, headers=headers)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['created'])

    def test_04_create_actor2(self):
        headers = {"Authorization": f"Bearer {self.director_token}",
                   "Content-Type": "application/json"}
        res = self.client.post('/actors', json=self.new_actor_2, headers=headers)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['created'])

    def test_05_create_actor3(self):
        headers = {"Authorization": f'Bearer {self.director_token}',
                   "Content-Type": "application/json"}
        res = self.client.post('/actors', json=self.new_actor_3, headers=headers)

        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['created'])

    def test_06_create_actor4(self):
        headers = {"Authorization": f'Bearer {self.director_token}',
                   "Content-Type": "application/json"}
        res = self.client.post('/actors', json=self.new_actor_4, headers=headers)

        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['created'])

    def test_07_get_actors(self):
        headers = {"Authorization": f"Bearer {self.assistant_token}"}
        res = self.client.get('/actors', headers=headers)
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['actors'])

    def test_08_get_movies(self):
        headers = {"Authorization": f"Bearer {self.assistant_token}"}
        res = self.client.get('/movies', headers=headers)
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['movies'])

    def test_09_update_actor(self):
        headers = {"Authorization": f"Bearer {self.director_token}"}
        res = self.client.patch('/actors/1', json={"age": 65}, headers=headers)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['updated'])

    def test_10_update_movie(self):
        headers = {"Authorization": f"Bearer {self.producer_token}"}
        res = self.client.patch('/movies/1', json={"title": "Forrest Gump"}, headers=headers)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['updated'])

    def test_11_delete_actor(self):
        headers = {"Authorization": f"Bearer {self.producer_token}"}
        res = self.client.delete('/actors/3', headers=headers)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['deleted'])

    def test_12_delete_movie(self):
        headers = {"Authorization": f"Bearer {self.producer_token}"}
        res = self.client.delete('/movies/2', headers=headers)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['deleted'])

    def test_13_422_if_actor_creation_fails(self):
        headers = {"Authorization": f"Bearer {self.director_token}"}
        res = self.client.post('/actors', json={}, headers=headers)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], "unprocessable")
    
    def test_14_422_if_movie_creation_fails(self):
        headers = {"Authorization": f"Bearer {self.producer_token}"}
        res = self.client.post('/movies', json={}, headers=headers)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], "unprocessable")

    def test_15_401_if_actor_deletion_fails(self):
        headers = {"Authorization": f"Bearer {self.assistant_token}"}
        res = self.client.delete('/actors/1', headers=headers)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 401)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message']['code'], "unauthorized")

    def test_16_401_if_movie_deletion_fails(self):
        headers = {"Authorization": f"Bearer {self.director_token}"}
        res = self.client.delete('/movies/1', headers=headers)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 401)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message']['code'], "unauthorized")

    def test_17_401_if_actor_creation_fails(self):
        headers = {"Authorization": f"Bearer {self.assistant_token}"}
        res = self.client.delete('/actors/1', headers=headers)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 401)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message']['code'], "unauthorized")

    def test_18_401_if_movie_creation_fails(self):
        headers = {"Authorization": f"Bearer {self.director_token}"}
        res = self.client.delete('/movies/1', headers=headers)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 401)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message']['code'], "unauthorized")

    def test_19_401_if_actor_update_fails(self):
        headers = {"Authorization": f"Bearer {self.assistant_token}"}
        res = self.client.delete('/actors/1', headers=headers)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 401)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message']['code'], "unauthorized")

    def test_20_401_if_movie_update_fails(self):
        headers = {"Authorization": f"Bearer {self.assistant_token}"}
        res = self.client.delete('/movies/1', headers=headers)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 401)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message']['code'], "unauthorized")
    
if __name__ == "__main__":
    unittest.main()
        

