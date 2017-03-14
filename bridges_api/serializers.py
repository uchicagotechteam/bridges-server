from django.contrib.auth.models import User
from rest_framework import serializers
from bridges_api.models import Question, UserProfile, Tag, Employer

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'password')

class UserProfileSerializer(serializers.ModelSerializer):
    username = serializers.ReadOnlyField(source='user.username')
    user_id = serializers.ReadOnlyField(source='pk')
    profile_picture = serializers.ImageField(max_length=None, allow_empty_file=False, use_url=True)

    class Meta:
        model = UserProfile
        fields = ('username', 'date_of_birth', 'gender',
                  'ethnicity', 'disabilities', 'current_employer',
                  'profile_picture', 'first_name', 'last_name',
                  'email', 'user_id')

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('attribute', 'value')

class QuestionSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True)
    class Meta:
        model = Question
        fields = ('id', 'title', 'description', 'answer',
                  'tags', 'number_of_views')

class EmployerSerializer(serializers.ModelSerializer):
    class Meta:
      model = Employer
      fields = ('name', 'address', 'rating',
                'averagesalary', 'questions')
