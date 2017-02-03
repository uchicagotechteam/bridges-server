from django.contrib.auth.models import User
from rest_framework import serializers
from bridges_api.models import Question, UserProfile, Tag, Employer

class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ('id', 'title', 'description', 'answer',
                  'tags', 'number_of_views')

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'password')

class UserProfileSerializer(serializers.ModelSerializer):
    username = serializers.ReadOnlyField(source='user.username')
    user_id = serializers.ReadOnlyField(source='pk')
    class Meta:
        model = UserProfile
        fields = ('username', 'date_of_birth', 'gender',
                  'ethnicity', 'disabilities', 'current_employer',
                  'first_name', 'last_name', 'email', 'user_id')

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('name')

class EmployerSerializer(serializers.ModelSerializer):
    class Meta:
      model = Employer
      fields = ('name', 'address', 'rating',
                'averagesalary', 'questions')
