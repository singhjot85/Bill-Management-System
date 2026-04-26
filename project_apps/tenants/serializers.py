from rest_framework.serializers import ModelSerializer
from django.contrib.auth import get_user_model

User = get_user_model()


# TODO: Figure out a way for public user registration
# Bigger question is, is that required ???
class UserSerializer(ModelSerializer):

    class Meta:
        model = User
        fields = []
        read_only_fields = []
    
    def create(self, validated_data):
        raise NotImplementedError()
    
    def update(self, instance, validated_data):
        raise NotImplementedError()