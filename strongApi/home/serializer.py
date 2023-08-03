from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
# def validate_username(value):
#     print(value)
#     if User.objects.filter(username = value).exists():
#         raise serializers.ValidationError("username already exist try another name","already")
# #     return value
#         extra_kwargs = {
#             'username' : {'min_length' : 3,'validators': [validate_username]},
#         }

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email','password']
        extra_kwargs = {
            'username' : {'min_length' : 3},
            'email' : {'allow_null' : True},
            'password' : {'write_only': True, 'min_length': 8}
        }
    def validate_password(self, value):
        # Custom password validation
        if ' ' in value:
            raise serializers.ValidationError("Password cannot contain spaces.")
        return value
    
    def create(self, validated_data):
        validated_data['password'] = make_password(validated_data['password'])
        return super().create(validated_data)

