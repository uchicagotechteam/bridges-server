import operator

from bridges_api.models import Question, UserProfile, Employer, Tag
from bridges_api.serializers import (
    QuestionSerializer,
    UserSerializer,
    UserProfileSerializer,
    TagSerializer,
    EmployerSerializer
)
from bridges_api.permissions import MustBeSuperUserToGET

from django.contrib.auth.models import User
from django.db.models import Q

from rest_framework import generics
from rest_framework import permissions
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.parsers import JSONParser
from rest_framework.authtoken.models import Token

def restrict_fields(query_dict, fields):
    """
    Filters the fields in a query_dict based on a list
    of strings
    """
    restricted_dict = {}
    for field in fields:
        if query_dict.get(field):
            restricted_dict[field] = query_dict.get(field)
    return restricted_dict

@api_view(['GET'])
def api_root(request, format=None):
    """
    This is the main page of the API for the Bridges to Work Virtual Mentor.
    """
    return Response({
        'users': reverse('user-list', request=request, format=format),
        'questions': reverse('question-list', request=request, format=format),
        'employers': reverse('employer-list', request=request, format=format),
        'tags': reverse('tag-list', request=request, format=format)
    })

class QuestionList(generics.ListAPIView):
    """
    This uses that generic API list view to return a list
    of Question models as a response to GET requests. The queryset
    variable is the list of Question Models that ultimately gets
    serialized and returned to the User
    """
    serializer_class = QuestionSerializer
    #permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        search_term = self.request.query_params.get('search')
        if (search_term):
            search_terms = search_term.split()
            queryset = list(Question.objects.filter(
                reduce(operator.and_, (Q(answer__contains = term) for term in search_terms)) |
                reduce(operator.and_, (Q(title__contains = term) for term in search_terms)) |
                reduce(operator.and_, (Q(description__contains = term) for term in search_terms))
            ))

            if (queryset):
                return queryset

        return Question.objects.all()



class QuestionDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    Returns the specific Question object with its corresponding id
    """
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    permission_classes = (permissions.IsAuthenticated,)

class UserList(generics.ListCreateAPIView):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = (MustBeSuperUserToGET,)

    def post(self, request, *args, **kwargs):
        """
        Overwritting POST request behavior so that creating a new user
        requires a unique username, a password, first name, last name,
        email address, birth date formatted as YYYY-MM-DD, disabilities, and gender
        """
        user_fields = UserSerializer().fields.keys()
        profile_fields = UserProfileSerializer().fields.keys()

        user_data = restrict_fields(request.data, user_fields)
        profile_data = restrict_fields(request.data, profile_fields)

        user_serializer = UserSerializer(data=user_data)
        profile_serializer = UserProfileSerializer(data=profile_data)

        if user_serializer.is_valid():
            if profile_serializer.is_valid():
               new_user = user_serializer.save()
               tethered_profile_serializer = UserProfileSerializer(new_user.userprofile,
                                                                   data=profile_data)
               if tethered_profile_serializer.is_valid():
                   tethered_profile_serializer.save()
                   token, created = Token.objects.get_or_create(user=new_user)

                   return Response({
                       'user_id': new_user.pk,
                       'token': token.key
                   }, status=status.HTTP_201_CREATED)

            return Response({
                'errors': profile_serializer.errors,
            }, status=status.HTTP_400_BAD_REQUEST)

        return Response({
            'errors': user_serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

class UserDetail(generics.RetrieveAPIView):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permissions = (permissions.IsAuthenticated,)

class TagList(generics.ListAPIView):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer

class EmployerList(generics.ListAPIView):
    queryset = Employer.objects.all()
    serializer_class = EmployerSerializer

class EmployerDetail(generics.RetrieveAPIView):
    queryset = Employer.objects.all()
    serializer_class = EmployerSerializer
