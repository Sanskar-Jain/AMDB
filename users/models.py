from django.db import models
import uuid

# Create your models here.


class users(models.Model):
    name = models.CharField(max_length=200, null=False, blank=False)
    username = models.CharField(max_length=100, unique=True, null=False, blank=False)
    password = models.CharField(max_length=200, null=False, blank=False)
    email = models.CharField(max_length=200, null=False, blank=False)
    short_bio = models.CharField(max_length=400)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

class token(models.Model):
    user_id = models.ForeignKey(users)
    access_token = models.CharField(max_length=255)
    created_on = models.DateTimeField(auto_now_add=True)
    last_request_on = models.DateTimeField(auto_now=True)
    is_valid = models.BooleanField(default=True)

    def create_token(self):
        self.access_token = uuid.uuid4()