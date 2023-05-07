from django.core.exceptions import ValidationError
from rest_framework import serializers
from rest_framework.exceptions import ParseError

from .models import Restaurant, Menu, Vote, User


# User Serializer
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email')

# Register Serializer
class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(validated_data['username'], validated_data['email'], validated_data['password'])

        return user

class RestaurantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Restaurant
        fields = ('name', 'address')


class MenuSerializer(serializers.ModelSerializer):

    class Meta:
        model = Menu
        fields = ('restaurant', 'day_of_week', 'dishes')

    def validate(self, attrs):
        days = ["Monday",
                "Tuesday",
                "Wednesday",
                "Thursday",
                "Friday",
                "Saturday",
                "Sunday",
                ]
        if attrs['day_of_week'] not in days:
            raise ValidationError('Invalid day of week')
        return attrs


class VoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vote
        fields = ('menu', 'employee')

    def validate(self, attrs):
        user = self.context['request'].user
        menu = attrs['menu']

        # Check if the user has already voted for this menu
        if Vote.objects.filter(user=user, menu=menu).exists():
            raise ParseError('You have already voted for this menu')

        # Check if the user is an employee
        if not user.groups.filter(name='employee').exists():
            raise ParseError('Only employees can vote')

        return attrs


class CurrentDayMenuSerializer(serializers.ModelSerializer):
    restaurant = RestaurantSerializer()

    class Meta:
        model = Menu
        fields = ('restaurant', 'dishes')
