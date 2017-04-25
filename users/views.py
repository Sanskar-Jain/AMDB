from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from users.models import users

from rest_framework.decorators import api_view
from rest_framework.response import Response
from users.serializers import UserSerializer

# Create your views here.


@api_view(["POST"])
def user_create(request):
    try:
        name = request.data["name"]
        username = request.data["username"]
        password = request.data["password"]
        email = request.data["email"]
        short_bio = request.data["short_bio"]
    except KeyError:
        return Response({"error_message": "KeyError! Please make sure you provide all Fields : name, username, password, email, short_bio."}, status = 400)

    if len(name) == 0 or name is None:
        return Response({"error_message": "Name Field cannot be left Empty!"}, status = 400)

    if len(password) < 6 or password is None:
        return Response({"error_message": "Password should be atleast 6 Characters long!"}, status = 400)

    user = users.objects.filter(username=username).first()

    if user != None:
        return Response({"error_message": "User with this Username already exists! Please Choose another Username."},status=400)

    new_user = users.objects.create(name = name, username = username, password = password, email = email, short_bio = short_bio)
    new_user.save()

    return Response(UserSerializer(instance=new_user).data, status=200)
