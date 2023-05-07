from django.test import TestCase
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient, APITestCase
from rest_framework_jwt.settings import api_settings
from django.urls import reverse
from rest_framework import status
from .models import Restaurant, Menu, Employee, Vote, User
from .serializers import MenuSerializer
from datetime import datetime


class AuthenticationTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='test_user',
            password='test_password'
        )
        self.client = APIClient()
        self.jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
        self.jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

    def test_valid_login(self):
        response = self.client.post('/api/v1/signin/', {'username': 'test_user', 'password': 'test_password'})
        self.assertEqual(response.status_code, 200)

    def test_invalid_login(self):
        payload = self.jwt_payload_handler(self.user)
        token = self.jwt_encode_handler(payload)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)

        response = self.client.get('/api/v1/restaurant/')
        self.assertEqual(response.status_code, 401)


class RevokeTokenTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.token = Token.objects.create(user=self.user)

    def test_revoke_token(self):
        # Revoke the token
        response = self.client.post(reverse('revoke'), {'token': self.token.key})
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


class RestaurantTestCase(TestCase):
    def test_create_restaurant(self):
        name = "Test Restaurant"
        address = "123 Main St"
        restaurant = Restaurant.objects.create(name=name, address=address)
        self.assertEqual(restaurant.name, name)
        self.assertEqual(restaurant.address, address)


class EmployeeTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='johndoe',
            email='johndoe@example.com',
            password='password123'
        )
        self.employee = Employee.objects.create(user=self.user)

    def test_employee_str_method(self):
        expected_str = self.employee.user.username
        self.assertEqual(str(self.employee), expected_str)


class MenuListTestCase(APITestCase):
    def setUp(self):
        # Create a user
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass',
        )
        # Create a restaurant for the user
        self.restaurant = Restaurant.objects.create(
            name='Test Restaurant',
            address='Test Address',
        )
        self.restaurant_user = self.restaurant.restaurantuser_set.create(user=self.user, restaurant=self.restaurant)

        # Create a menu for the restaurant
        self.menu_data = {
            'restaurant': self.restaurant,
            'day_of_week': 'Monday',
            'dishes': 'Test Dish',
        }
        self.menu = Menu.objects.create(**self.menu_data)

        # Set up authentication
        self.client.force_authenticate(user=self.user)

    def test_list_menus(self):
        url = reverse('menu')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        serializer_data = MenuSerializer([self.menu], many=True).data
        self.assertEqual(response.data, serializer_data)

    def test_create_menu(self):
        url = reverse('menu')
        new_menu_data = {
            'restaurant': self.restaurant.id,
            'day_of_week': 'Tuesday',
            'dishes': 'New Dish',
        }
        response = self.client.post(url, new_menu_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        new_menu = Menu.objects.filter(day_of_week='Tuesday').first()
        self.assertIsNotNone(new_menu)
        self.assertEqual(new_menu.restaurant, self.restaurant)
        self.assertEqual(new_menu.dishes, 'New Dish')

    def test_create_menu_with_invalid_data(self):
        url = reverse('menu')
        invalid_data = {
            'day_of_week': 'Invalid Day',
            'dishes': 'New Dish',
        }
        response = self.client.post(url, invalid_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_menu(self):
        url = reverse('menu')
        update_data = {
            'id': self.menu.id,
            'restaurant': self.menu.restaurant.id,
            'day_of_week': 'Monday',
            'dishes': 'Updated Dish',
        }
        response = self.client.put(url, update_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.menu.refresh_from_db()
        self.assertEqual(self.menu.dishes, 'Updated Dish')

    def test_update_menu_with_invalid_data(self):
        url = reverse('menu')
        invalid_data = {
            'day_of_week': 'Invalid Day',
            'dishes': 'Updated Dish',
        }
        response = self.client.put(url, invalid_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_menu_with_nonexistent_menu(self):
        url = reverse('menu')
        update_data = {
            'day_of_week': 'Sunday',
            'dishes': 'Updated Dish',
        }
        response = self.client.put(url, update_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def tearDown(self):
        self.client.force_authenticate(user=None)


class CurrentDayMenuTestCase(APITestCase):
    def setUp(self):
        # Create a user
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass',
        )

        # Create a restaurant for the user
        self.restaurant = Restaurant.objects.create(
            name='Test Restaurant',
            address='Test Address',
        )
        self.restaurant_user = self.restaurant.restaurantuser_set.create(user=self.user)

        # Set up authentication
        self.client.force_authenticate(user=self.user)

    def test_get_current_day_menu(self):
        url = reverse('menu-today')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        today = datetime.now().strftime("%A")
        menu = Menu.objects.filter(restaurant=self.restaurant, day_of_week=today).first()
        serializer_data = MenuSerializer(menu).data
        self.assertEqual(response.data, serializer_data)

    def tearDown(self):
        self.client.force_authenticate(user=None)


class VoteTestCase(APITestCase):
    def setUp(self):

        # Create user
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass'
        )

        # Create restaurant
        self.restaurant = Restaurant.objects.create(
            name='Test Restaurant',
            address='123 Test St'
        )

        # Create menu for restaurant
        self.menu = Menu.objects.create(
            restaurant=self.restaurant,
            day_of_week='Monday',
            dishes='Test Dish 1\nTest Dish 2'
        )
        # Set up authentication
        self.client.force_authenticate(user=self.user)

        # Create employee and associate with user
        self.employee = Employee.objects.create(user=self.user)

    def test_vote_creation(self):
        # Ensure a vote can be created for an employee and menu
        vote = Vote.objects.create(employee=self.employee, menu=self.menu)
        self.assertEqual(vote.employee, self.employee)
        self.assertEqual(vote.menu, self.menu)

    def test_vote_creation_without_authentication(self):
        url = reverse('vote')
        data = {'menu': self.menu.id}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Vote.objects.count(), 0)

    def test_vote_creation_with_invalid_menu_id(self):
        url = reverse('vote')
        data = {'menu': 100}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Vote.objects.count(), 0)

    def test_vote_creation_with_existing_vote(self):
        vote = Vote.objects.create(menu=self.menu, employee=self.employee)
        url = reverse('vote')
        data = {'menu': self.menu.id}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Vote.objects.count(), 1)



