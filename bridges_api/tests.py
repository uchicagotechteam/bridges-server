from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIRequestFactory
from rest_framework.test import APITestCase
from rest_framework.test import APIClient
from bridges_api.models import Question

class QuestionTests(APITestCase):
    bridges_client = APIClient()

    def test_get_question(self):
        """
        Make sure getting question returns the whole question properly
        """
        test_title = 'Where does the muffin man live?'
        test_description = 'Many have seen the muffin man,\
        but few know where he resides'
        test_answer = 'The muffin man lives on cherry lane'
        test_tags = 'fairies, baking, cooking'
        test_num_views = 1025

        Question.objects.create(title=test_title, description=test_description,
        answer=test_answer, tags=test_tags, number_of_views=test_num_views)
        saved_question = Question.objects.get()

        response = self.bridges_client.get('/questions/')
        returned_question = response.json()['results'][0]

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(returned_question['title'], saved_question.title)
        self.assertEqual(returned_question['description'], saved_question.description)
        self.assertEqual(returned_question['answer'], saved_question.answer)
        self.assertEqual(returned_question['tags'], saved_question.tags)
        self.assertEqual(returned_question['number_of_views'], saved_question.number_of_views)

    def test_post_question(self):
        """
        Make sure that POST requests are not allowed (i.e questions can't be created)
        """

        data = {
            'title': "Why don't we support creating questions via POST?",
            'answer': "That's a big burden for the mobile team, and is not in the MVP"
        }

        response = self.bridges_client.post('/questions/', data, format='json')

        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
