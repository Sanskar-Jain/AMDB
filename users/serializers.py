from rest_framework.serializers import ModelSerializer
from users.models import users,movies


class UserSerializer(ModelSerializer):

    class Meta:
        model = users
        fields = ('id', 'name', 'username', 'email', 'short_bio', 'created_on', 'updated_on')


class MovieSerializer(ModelSerializer):

    class Meta:
        model = movies
        fields = ('name', 'duration_in_minutes', 'release_date', 'overall_rating', 'censor_board_rating', 'profile_pic_url')