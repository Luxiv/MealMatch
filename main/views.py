from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from rest_framework import status
from datetime import datetime
from knox.models import AuthToken
from rest_framework.authtoken.models import Token
from .models import RestaurantUser, Menu, Vote, User, Restaurant
from .serializers import MenuSerializer, VoteSerializer, RestaurantSerializer, UserSerializer, RegisterSerializer


# Register API
class RegisterAPI(generics.GenericAPIView):
    serializer_class = RegisterSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response({
            "user": UserSerializer(user, context=self.get_serializer_context()).data,
            "token": AuthToken.objects.create(user)[1]
        })


class SignInView(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = User.objects.filter(username=username).first()
        if user is None:
            return Response({'error': 'Invalid username or password'}, status=status.HTTP_401_UNAUTHORIZED)
        if not user.check_password(password):
            return Response({'error': 'Invalid username or password'}, status=status.HTTP_401_UNAUTHORIZED)
        token = Token.objects.create(user=user)
        return Response({'token': token})


class RevokeTokenView(APIView):

    def post(self, request, format=None):
        token = request.data.get('token')
        if not token:
            return Response({'error': 'Token is required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            token = Token.objects.get(key=token)
        except Token.DoesNotExist:
            return Response({'error': 'Invalid token.'}, status=status.HTTP_400_BAD_REQUEST)

        token.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# Restaurant
class RestaurantCreateView(generics.CreateAPIView):
    queryset = Restaurant.objects.all()
    serializer_class = RestaurantSerializer
    authentication_classes = (JSONWebTokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class MenuListView(generics.ListAPIView):
    queryset = Menu.objects.all()
    serializer_class = MenuSerializer
    authentication_classes = (JSONWebTokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        restaurant = RestaurantUser.objects.filter(user=request.user).first()
        if not restaurant:
            return Response({'error': 'No restaurant found for the user'}, status=status.HTTP_400_BAD_REQUEST)

        data = request.data.copy()
        data['restaurant'] = restaurant.id
        serializer = MenuSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def put(self, request):
        restaurant = RestaurantUser.objects.filter(user=request.user).first()
        if not restaurant:
            return Response({'error': 'No restaurant found for the user'}, status=status.HTTP_400_BAD_REQUEST)

        day_of_week = request.data.get('day_of_week')
        menu = Menu.objects.filter(restaurant=restaurant.restaurant, day_of_week=day_of_week).first()
        if not menu:
            return Response({'error': 'No menu found for the given day'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = MenuSerializer(menu, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class CurrentDayMenuView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, format=None):
        today = datetime.now().strftime('%A')
        menus = Menu.objects.filter(day_of_week=today)
        serializer = MenuSerializer(menus, many=True)
        return Response(serializer.data)


class VoteView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, format=None):
        employee = request.user.employee
        if not employee:
            return Response({'error': 'User is not an employee'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            menu_id = request.data['menu'].id
            day_of_week = request.data.get('day_of_week')
            menu = Menu.objects.get(id=menu_id, day_of_week=day_of_week)
        except:
            return Response({'error': 'Invalid menu ID'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            vote = Vote.objects.get(employee=employee, menu__day_of_week=day_of_week)
            vote.menu = menu
            vote.save()
        except Vote.DoesNotExist:
            vote = Vote.objects.create(employee=employee, menu=menu)
        serializer = VoteSerializer(vote)
        return Response(serializer.data)


class ResultsView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, format=None):
        today = datetime.now().strftime('%A')
        votes = Vote.objects.filter(menu__day_of_week=today)
        serializer = VoteSerializer(votes, many=True)
        return Response(serializer.data)
