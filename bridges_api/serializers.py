from django.contrib.auth.models import User
from rest_framework import serializers
from bridges_api.models import Question, UserProfile, Tag, Employer

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

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'password')

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        instance = self.Meta.model(**validated_data)
        if password is not None:
            instance.set_password(password)
        instance.save()
        return instance

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            if attr == 'password':
                instance.set_password(value)
            else:
                setattr(instance, attr, value)
        instance.save()
        return instance

class UserProfileSerializer(serializers.ModelSerializer):
    username = serializers.ReadOnlyField(source='user.username')
    user_id = serializers.ReadOnlyField(source='pk')

    class Meta:
        model = UserProfile
        fields = ('username', 'date_of_birth', 'gender',
                  'ethnicity', 'disabilities', 'current_employer',
                  'profile_picture', 'position', 'first_name',
                  'last_name', 'email', 'user_id', 'bookmarks')

class EmployerSerializer(serializers.ModelSerializer):
    class Meta:
      model = Employer
      fields = ('name', 'address', 'rating',
                'averagesalary', 'questions')
