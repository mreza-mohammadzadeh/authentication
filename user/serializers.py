from rest_framework import serializers
from user.models import User


class UserCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'firstname', 'lastname', 'gender']


class UserListSerializer(serializers.ModelSerializer):
    gender = serializers.CharField(source='get_gender_display')

    class Meta:
        model = User
        fields = ['id', 'username', 'firstname', 'lastname', 'gender', 'birthday']


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'firstname', 'lastname', 'gender', 'birthday']

