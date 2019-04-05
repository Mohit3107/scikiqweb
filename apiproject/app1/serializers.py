from km.models import *
from rest_framework import serializers

class UserSerializer(serializers.ModelSerializer):    
    class Meta:
        model = User
        fields = ('id','email', 'password',  'is_active', 'id', 'apikey', 'is_block', 'is_delete')
        write_only_fields = ('password',)  

class UserProfileSerializer(serializers.ModelSerializer):
    email_detail = serializers.RelatedField('getEmail')
    class Meta:
        model = UserProfile
        exclude = ('user','id')