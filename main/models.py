from django.db import models
from django.contrib.auth.models import AbstractUser


class Restaurant(models.Model):
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Menu(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    day_of_week = models.CharField(max_length=255)
    dishes = models.TextField()

    class Meta:
        unique_together = ('restaurant', 'day_of_week')

    def __str__(self):
        return f"{self.restaurant.name} - {self.day_of_week}"


class User(AbstractUser):
    is_employee = models.BooleanField(default=False)
    is_restaurant_user = models.BooleanField(default=False)
    password2 = models.CharField(max_length=128)


class Employee(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.username


class RestaurantUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.username} - {self.restaurant.name}"


class Vote(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    menu = models.ForeignKey(Menu, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.employee.user.username} - {self.menu.restaurant.name} - {self.menu.day_of_week}"
