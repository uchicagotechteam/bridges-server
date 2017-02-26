from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIRequestFactory
from rest_framework.test import APITestCase
from rest_framework.test import APIClient
from bridges_api.models import Question

def set_auth(bridges_client):
    bridges_client.credentials()
    data = {
        "username": "testUser123",
        "password": "testPassword",
        "date_of_birth": "2014-01-01",
        "gender": "male",
        "ethnicity": "n/a",
        "disabilities": "n/a",
        "current_employer": "n/a",
        "first_name": "test",
        "last_name": "user",
        "email": "test@user.mail"
    }
    response = bridges_client.post('/users/', data, format='json')
    if response.status_code != status.HTTP_201_CREATED: # User already exists
        data = {
            "username": "testUser123",
            "password": "testPassword"
        }
        response = bridges_client.post('/api-token-auth/', data, format='json')

    token = response.json()["token"]
    bridges_client.credentials(HTTP_AUTHORIZATION='Token ' + token)

class QuestionTests(APITestCase):
    bridges_client = APIClient()

    def test_get_question(self):
        """
        Make sure getting question returns the whole question properly
        """
        set_auth(self.bridges_client)
        test_title = 'Where does the muffin man live?'
        test_description = 'Many have seen the muffin man,\
        but few know where he resides'
        test_answer = 'The muffin man lives on cherry lane'
        test_num_views = 1025


        Question.objects.create(title=test_title, description=test_description,
        answer=test_answer, number_of_views=test_num_views)
        saved_question = Question.objects.get()

        response = self.bridges_client.get('/questions/')
        returned_question = response.json()['results'][0]

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(returned_question['title'], saved_question.title)
        self.assertEqual(returned_question['description'], saved_question.description)
        self.assertEqual(returned_question['answer'], saved_question.answer)
        self.assertEqual(returned_question['number_of_views'], saved_question.number_of_views)

    def test_post_question(self):
        """
        Make sure that POST requests are not allowed (i.e questions can't be created)
        """
        set_auth(self.bridges_client)
        data = {
            'title': "Why don't we support creating questions via POST?",
            'answer': "That's a big burden for the mobile team, and is not in the MVP"
        }

        response = self.bridges_client.post('/questions/', data, format='json')

        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

class UserTests(APITestCase):
    bridges_client = APIClient()

    def test_token_authentication(self):
        """
        Ensure that tokens are received upon user creation and can be used to
        access pages that require permissions.
        """
        response = self.bridges_client.get('/questions/')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        set_auth(self.bridges_client)
        response = self.bridges_client.get('/questions/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        invalid = "2b222ce510a9a2c17b3b973ec5b053c5a45b0391"
        self.bridges_client.credentials(HTTP_AUTHORIZATION='Token '+invalid)
        response = self.bridges_client.get('/questions/')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
