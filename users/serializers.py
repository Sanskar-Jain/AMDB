from rest_framework.serializers import ModelSerializer
from users.models import users


class UserSerializer(ModelSerializer):

    class Meta:
        model = users
        fields = ('id', 'name', 'username', 'email', 'short_bio', 'created_on', 'updated_on')