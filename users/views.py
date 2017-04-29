from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.hashers import make_password, check_password
from users.models import users, token, movies, genre, moviegenre
from datetime import datetime
import pprint
import json

from rest_framework.decorators import api_view
from rest_framework.response import Response
from users.serializers import UserSerializer, MovieSerializer

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


def check_token(request):
    try:
        access_token = request.META['HTTP_TOKEN']
    except KeyError:
        return 'KeyError'

    token_exists = token.objects.filter(access_token=access_token, is_valid=True).first()

    if not token_exists:
        return None

    return token_exists.user_id


@api_view(["POST"])
def create_movie(request):
    current_user = check_token(request)

    if current_user == None:
        return Response({"error_message": "You are not Authorized to perform this Action."}, status=400)

    if current_user == 'KeyError':
        return Response({"error_message": "Access Token not found in Header.Please pass it as 'token'"}, status=400)

    try:
        name = request.data["name"]
        duration_in_minutes = request.data['duration_in_minutes']
        release_date = request.data['release_date']
        censor_board_rating = request.data['censor_board_rating']
        profile_pic_url = request.data['profile_pic_url']
        genres = request.data['genre']

        try:
            duration_in_minutes = int(duration_in_minutes)
        except:
            return Response({"error_message" : "duration_in_minutes should be an Integer."}, status=400)

        try:
            censor_board_rating = float(censor_board_rating)
        except:
            return Response({"error_message" : "censor_board_rating should be a Decimal Number."}, status=400)

    except KeyError:
        return Response({"error_message" : "Please make sure you provide all fields : name, duration_in_minutes, release_date, censor_board_rating, profile_pic_url, genre"}, status=400)

    if len(name) == 0:
        return Response({"error_message" : "Name Field cannot be left empty."}, status=400)

    movie_exists = movies.objects.filter(name=name).first()

    if movie_exists:
        return Response({"error_message" : "Movie already exists."}, status=400)

    if not release_date:
        return Response({"error_message" : "release_date cannot be left Empty."}, status=400)

    if not censor_board_rating:
        return Response({"error_message" : "censor_board_rating cannot be left Empty."}, status=400)

    if not profile_pic_url:
        return Response({"error_message" : "profile_pic_url cannot be left Empty."}, status=400)

    if duration_in_minutes <= 0:
        return Response({"error_message" : "duration_in_minutes should be greater than zero."}, status=400)

    if len(genres) == 0:
        return Response({"error_message" : "Every movie should have atleast one genre attached to it."}, status=400)

    try:
        release_date = datetime.strptime(release_date, "%Y-%m-%d")
    except:
        return Response({"error_message" : "Please Enter Date in 'yyyy-mm-dd' Format"}, status=400)

    movie = movies.objects.create(name=name, duration_in_minutes=duration_in_minutes, release_date=release_date, overall_rating=0, censor_board_rating=censor_board_rating, profile_pic_url=profile_pic_url, user_id=current_user)
    movie.save()

    for i in genres:
        genre_string = genre.objects.filter(name=i).first()
        map_movie_genre = moviegenre.objects.create(movie_id=movie, genre_id=genre_string)

    return Response(MovieSerializer(instance=movie).data, status=200)


@api_view(["GET"])
def list_movie(request):

    query = request.query_params

    if len(query) == 0:
        movie = movies.objects.all()
        return Response(MovieSerializer(instance=movie, many=True).data, status=200)

    elif 'q' in query.keys() and len(query['q']) == 0:
        return Response({"error_message": "query parameter 'q' not found in url while processing GET request!"}, status=400)

    elif 'q' in query.keys():
        search = str(query['q'])

        movie = movies.objects.filter(name__icontains=search)

        genre_movie = genre.objects.filter(name__icontains=search)

        movie_list = []
        movie_list_names = []

        if genre_movie is not None:
            for each_genre in genre_movie:
                id = each_genre.id
                movie_for_genre = moviegenre.objects.filter(genre_id=id)

                for i in movie_for_genre:
                    movie_list.append(MovieSerializer(instance=i.movie_id).data)
                    movie_list_names.append(i.movie_id.name)

        if movie is not None:
            for each_movie in movie:
                if each_movie.name not in movie_list_names:
                    movie_list.append(MovieSerializer(instance=each_movie).data)
                    movie_list_names.append(each_movie.name)

        if len(movie_list) == 0:
            return Response({"error_message": "No Movies found!"})

        return HttpResponse(json.dumps(movie_list, indent=4))

    else:
        return Response({"error_message": "query parameter 'q' containing search word not found in url while processing get request!"}, status=400)


@api_view(["POST"])
def review_movie(request):
    current_user = check_token(request)

