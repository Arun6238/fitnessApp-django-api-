from home.models import Exercise,Instruction,CustomeExercise
from rest_framework import serializers
from django.contrib.auth.models import User



class ExerciseSerializer(serializers.ModelSerializer):
    class Meta:
        model= Exercise
        fields = '__all__'

class CustomExerciseSerializer(serializers.ModelSerializer):
    class Meta:
        model= CustomeExercise
        fields = '__all__'
        
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User  # Replace with your actual User model
        fields = ['id', 'username', 'email']

class AllExerciseSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField(max_length=100)
    body_part = serializers.CharField(max_length=50,)
    category = serializers.CharField(max_length=50)
    image = serializers.URLField(required= False)
    user = UserSerializer(required=False)

    is_custom = serializers.SerializerMethodField()

    def get_is_custom(self, obj):
        return hasattr(obj,'user')
