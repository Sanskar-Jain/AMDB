from django.db import models
import uuid

# Create your models here.


# Model to Store Details of User.
class users(models.Model):
    name = models.CharField(max_length=200, null=False, blank=False)
    username = models.CharField(max_length=100, unique=True, null=False, blank=False)
    password = models.CharField(max_length=200, null=False, blank=False)
    email = models.CharField(max_length=200, null=False, blank=False)
    short_bio = models.CharField(max_length=400)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)


# Model to store Details about an Access Token.
class token(models.Model):
    user_id = models.ForeignKey(users,on_delete=models.CASCADE)
    access_token = models.CharField(max_length=255)
    created_on = models.DateTimeField(auto_now_add=True)
    last_request_on = models.DateTimeField(auto_now=True)
    is_valid = models.BooleanField(default=True)

    def create_token(self):
        self.access_token = uuid.uuid4()


# Model to Store Details of Movies.
class movies(models.Model):
    name = models.CharField(max_length=300)
    duration_in_minutes = models.IntegerField(default=120)
    release_date = models.DateTimeField()
    overall_rating = models.DecimalField(decimal_places=2, max_digits=4)
    censor_board_rating = models.CharField(max_length=5)
    profile_pic_url = models.CharField(max_length=300)
    user_id = models.ForeignKey(users,on_delete=models.CASCADE)


# Model to store Various Genre.
class genre(models.Model):
    name = models.CharField(max_length=200)


# Mapping Table
class moviegenre(models.Model):
    movie_id = models.ForeignKey(movies,on_delete=models.CASCADE)
    genre_id = models.ForeignKey(genre,on_delete=models.CASCADE)


# Model to Store Review of Movies.
class reviews(models.Model):
    user_id = models.ForeignKey(users,on_delete=models.CASCADE)
    movie_id = models.ForeignKey(movies,on_delete=models.CASCADE)
    rating = models.DecimalField(max_digits=4, decimal_places=2)
    review = models.CharField(max_length=300)