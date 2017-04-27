from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.hashers import make_password, check_password
from users.models import users, token

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

    new_user = users.objects.create(name = name, username = username, password = make_password(password), email = email, short_bio = short_bio)
    new_user.save()

    return Response(UserSerializer(instance=new_user).data, status=200)


@api_view(["GET"])
def get_user(request):
    query = request.query_params
    if len(query) == 0:
        user = users.objects.all()
        return Response(UserSerializer(instance=user, many=True).data, status=200)
    elif 'user_id' in query.keys() and len(query['user_id']) == 0:
        return Response({"error_message" : "user_id not found in url while processing GET request!"}, status=400)
    elif 'user_id' in query.keys() and not query['user_id'][0].isdigit():
        return Response({"error_message" : "user_id should be an Integer!"}, status=400)
    elif 'user_id' in query.keys():
        id = int(query['user_id'])
        user = users.objects.filter(id = id).first()

        if user == None:
            return Response({"error_message" : "User not found!"})

        return Response(UserSerializer(instance=user).data, status=200)
    else:
        return Response({"error_message" : "user_id not found in url while processing get request!"}, status=400)


@api_view(["POST"])
def login_user(request):
    try:
        username = request.data["username"]
        password = request.data["password"]
    except KeyError:
        return Response({"error_message": "Username or Password not provided! Invalid Request."}, status = 400)

    user = users.objects.filter(username = username).first()

    if user == None:
        return Response({"error_message" : "Invalid Username or Password."}, status=400)

    if not check_password(password, user.password):
        return Response({"error_message" : "Invalid Username or Password."}, status=400)

    access_token = token(user_id=user)
    access_token.create_token()
    access_token.save()

    return Response({"access_token" : access_token.access_token}, status=200)
