import operator

from django.contrib.auth.models import User
from django.db.models import Q

from rest_framework import generics
from rest_framework import permissions, authentication
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.parsers import JSONParser
from rest_framework.renderers import JSONRenderer
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView

from bridges_api.models import Question, UserProfile, Employer, Tag, Position, Ethnicity, Gender, Disability
from bridges_api.serializers import (
    QuestionSerializer,
    UserSerializer,
    UserProfileSerializer,
    TagSerializer,
    EmployerSerializer,
    PositionSerializer,
    EthnicitySerializer,
    DisabilitySerializer,
    GenderSerializer
)

from .permissions import MustBeSuperUserToGET, IsOwnerOrCreateOnly

from bridges_api import recommendations

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
    This is the main page of the API for the Bridges from School to Work virtual\
    mentor.
    The API provides access to questions, employers, and users.
    It can also recommend questions based on a user's profile.
    """
    return Response({
        'users': reverse('user-list', request=request, format=format),
        'user-info': reverse('user-info', request=request, format=format),
        'bookmarks': reverse('bookmarks', request=request, format=format),
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

    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        search_term = self.request.query_params.get('search')

        # searching takes precendence over recommending
        if (search_term and self.request.method == 'GET'):
            queryset = Question.objects.filter(
                Q(answer__icontains = search_term) |
                Q(title__icontains = search_term) |
                Q(description__icontains = search_term)
            )

            return queryset

        # If we're not searching, send back some recommendations
        try:
            profile = UserProfile.objects.get(user=self.request.user)
        except UserProfile.DoesNotExist:
            profile = None

        if (profile):
            return recommendations.recommend(profile, Question)
        else:
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
        user_data = restrict_fields(request.data, user_fields)
        user_serializer = UserSerializer(data=user_data)

        profile_fields = UserProfileSerializer().fields.keys()
        profile_data = restrict_fields(request.data, profile_fields)
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
    permission_classes = (permissions.IsAuthenticated, IsOwnerOrCreateOnly)

    def get(self, request, *args, **kwargs):
        """
        If you have your token, and you are the person hitting /user-info/,
        then you'll receive your own info.
        """
        try:
            requested_profile = UserProfile.objects.get(user=request.user)
        except:
            return Response({
                'errors': 'There is no profile corresponding to those credentials'
            }, status=status.HTTP_404_NOT_FOUND)

        self.check_object_permissions(request, requested_profile)
        serialized_profile = UserProfileSerializer(requested_profile)
        return Response(serialized_profile.data)

class BookmarksManager(APIView):
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, format=None):
        """
        Get the bookmarks associated with the user who is querying
        """
        profile = UserProfile.objects.get(user=request.user)
        serialized_bookmarks = QuestionSerializer(profile.bookmarks.all(), many=True)
        return Response({
            'bookmarks': JSONRenderer().render(serialized_bookmarks.data)
        }, status=status.HTTP_200_OK)

    def post(self, request, format=None):
        """
        Set the bookmarks on the user who is querying based on question ids
        If any of the question ids are invalid, raise an error and add none
        """
        profile = UserProfile.objects.get(user=request.user)
        bookmark_ids = request.data.get('bookmarks')

        # If we really post an empty list, clear bookmarks
        if (bookmark_ids == []):
            profile.bookmarks.clear()
            return Response({
                'response': 'bookmarks cleared successfully'
            })

        # If we're not posting an empty list
        # we only clear the bookmarks if the request succeeds
        elif (bookmark_ids):
            try:
                requested_bookmarks = Question.objects.filter(id__in=bookmark_ids)
                if len(requested_bookmarks) > 0:
                    profile.bookmarks.clear()
                    profile.bookmarks.add(*requested_bookmarks)
                    profile.save()
                    return Response({
                        'response': 'bookmarks set successfully'
                    }, status=status.HTTP_200_OK)
            except:
                return Response({
                    'error': 'One or more of the question ids does not exist'
                }, status=status.HTTP_404_NOT_FOUND)

        return Response({
            'error': 'Must include bookmarks field on request\
            with desired bookmarks to set'
        }, status=status.HTTP_400_BAD_REQUEST)

class TagList(generics.ListAPIView):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer

class PositionList(generics.ListAPIView):
    queryset = Position.objects.all()
    serializer_class = PositionSerializer

class EthnicityList(generics.ListAPIView):
    queryset = Ethnicity.objects.all()
    serializer_class = EthnicitySerializer

class GenderList(generics.ListAPIView):
    queryset = Gender.objects.all()
    serializer_class = GenderSerializer

class EmployerList(generics.ListAPIView):
    queryset = Employer.objects.all()
    serializer_class = EmployerSerializer

class DisabilityList(generics.ListAPIView):
    queryset = Disability.objects.all()
    serializer_class = DisabilitySerializer

class EmployerDetail(generics.RetrieveAPIView):
    queryset = Employer.objects.all()
    serializer_class = EmployerSerializer
