from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIRequestFactory
from rest_framework.test import APITestCase
from rest_framework.test import APIClient
from bridges_api.models import Question, UserProfile
from bridges_api import recommendations

from django.contrib.auth.models import User

example_user_data = {
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

def set_auth(bridges_client, data=example_user_data):
    bridges_client.credentials()
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
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        returned_question = response.json()['results'][0]

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

    def test_search_question(self):
        """
        Tests searching for questions via text
        """
        set_auth(self.bridges_client)
        test_title = 'Where does the muffin man live?'
        test_description = 'Many have seen the muffin man,\
        but few know where he resides'
        test_answer = 'The muffin man lives on cherry lane'
        test_num_views = 1025


        Question.objects.create(title=test_title, description=test_description,
        answer=test_answer, number_of_views=test_num_views)

        test_title2 = "How much wood could a woodchuck chuck?"
        test_description2 = "Woodchucks are indigenous to the swamp"
        test_answer2 = "A lot of wood"

        Question.objects.create(title=test_title2, description=test_description2,
        answer=test_answer2, number_of_views=test_num_views)

        response = self.bridges_client.get('/questions/', {'search': 'wood'})
        returned_questions = response.json()['results']
        self.assertEqual(len(returned_questions), 1)
        self.assertEqual(returned_questions[0].get('title'), test_title2)

        response = self.bridges_client.get('/questions/', {'search': 'the'})
        returned_questions = response.json()['results']
        self.assertEqual(len(returned_questions), 2)

        response = self.bridges_client.get('/questions/', {'search': 'Where does the muffin'})
        returned_questions = response.json()['results']
        self.assertEqual(len(returned_questions), 1)

        response = self.bridges_client.get('/questions/', {'search': 'Bkk'})
        returned_questions = response.json()['results']
        self.assertEqual(len(returned_questions), 0)

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

    def test_user_info(self):
        """
        Ensure that /user-info/ endpoint returns the proper user when queried
        """
        response = self.bridges_client.get('/user-info/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        set_auth(self.bridges_client)
        response = self.bridges_client.get('/user-info/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.json()
        self.assertEqual(results.get('username'), 'testUser123')
        self.assertEqual(results.get('gender'), 'male')

        data = {
            "username": "testUser345",
            "password": "testPassword",
            "date_of_birth": "2014-01-01",
            "gender": "male",
            "ethnicity": "n/a",
            "disabilities": "n/a",
            "current_employer": "n/a",
            "first_name": "test",
            "last_name": "user",
            "email": "test2@user.mail"
        }

        response = self.bridges_client.post('/users/', data, format='json')

        # If we try another token, we should get the info for that user
        self.bridges_client.credentials(HTTP_AUTHORIZATION='Token ' + response.json()['token'])
        response = self.bridges_client.get('/user-info/')
        results = response.json()
        self.assertEqual(results['username'], 'testUser345')

    def test_create_new_user(self):
        data = {
            "username": "testUser111",
            "password": "testPassword",
            "date_of_birth": "2014-01-01",
            "gender": "male",
            "ethnicity": "n/a",
            "disabilities": "n/a",
            "current_employer": "n/a",
            "first_name": "Stefan",
            "last_name": "Lance",
            "email": "test2@user.mail"
        }

        response = self.bridges_client.post('/users/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        user_obj = User.objects.get(username="testUser111")
        profile = UserProfile.objects.get(user=user_obj)

        self.assertEqual(profile.first_name, 'Stefan')
        self.assertEqual(profile.last_name, 'Lance')

class RecommendationsTests(APITestCase):
    bridges_client = APIClient()

    def test_insert(self):
        out_of_order = [("question17",17),("question16",16),("question15",15),
                        ("question17b",17),("question30",30),("question8",8),
                        ("question7",7),("question6",6),("question29",29),
                        ("question17c",17),("question28",28),("question4",4),
                        ("question27",27),("question23",23),("question14",14),
                        ("question22",22),("question21",21),("question18",18),
                        ("question13",13),("question12",12),("question20",20),
                        ("question19",19),("question11",11),("question10",10),
                        ("question9",9),("question4",4),("question26",26),
                        ("question25",25),("question24",24),("question14b",14),
                        ("question5",5)]
        in_order = [('question14',14),('question14b',14),('question15',15),
                         ('question16',16),('question17',17),('question17b',17),
                         ('question17c',17),('question18',18),('question19',19),
                         ('question20',20),('question21',21),('question22',22),
                         ('question23',23),('question24',24),('question25',25),
                         ('question26',26),('question27',27),('question28',28),
                         ('question29',29),('question30',30)]
        test_order = []
        for q in out_of_order :
            recommendations.insertQuestion(q,test_order)

        self.assertEqual(in_order,test_order)

    def test_removescores(self):
        in_order = [('question14',14),('question14b',14),('question15',15),
                         ('question16',16),('question17',17),('question17b',17),
                         ('question17c',17),('question18',18),('question19',19),
                         ('question20',20),('question21',21),('question22',22),
                         ('question23',23),('question24',24),('question25',25),
                         ('question26',26),('question27',27),('question28',28),
                         ('question29',29),('question30',30)]

        in_order_just_questions = ['question30','question29','question28',
                        'question27','question26','question25','question24',
                        'question23','question22','question21','question20',
                        'question19','question18','question17c','question17b',
                        'question17','question16','question15','question14b',
                        'question14']
        remove_score_list = recommendations.removeScoresFromList(in_order)

        self.assertEqual(in_order_just_questions, remove_score_list)

class BookmarkTests(APITestCase):
    bridges_client = APIClient()

    def test_set_bookmarks(self):
        set_auth(self.bridges_client)

        # Should override bookmarks on server w/ question ids
        data = {
            'bookmarks': [1, 2, 3, 4, 5]
        }

        response = self.bridges_client.post('/bookmarks/', data, format='json')

        # If the question ids are invalid, we should let the client know
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        question_data = [{'id': x, 'title': 'title' + str(x)} for x in range(1, 6)]
        for question in question_data:
            Question.objects.create(id=question['id'], title=question['title'])

        response = self.bridges_client.post('/bookmarks/', data, format='json')

        # If there are questions with the given ids, we're all good
        self.assertEqual(response.status_code, status.HTTP_200_OK)


    def test_get_bookmarks(self):
        set_auth(self.bridges_client)

        question_data = [{'id': x, 'title': 'title' + str(x)} for x in range(1, 6)]
        for question in question_data:
            Question.objects.create(id=question['id'], title=question['title'])

        profile = UserProfile.objects.get(user=User.objects.get(username='testUser123'))
        questions = Question.objects.filter(id__in=range(0, 6))

        for question in questions:
            profile.bookmarks.add(question)

        response = self.bridges_client.get('/bookmarks/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Response should contain the questions associated with that user's bookmarks
