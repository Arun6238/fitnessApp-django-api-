from django.contrib.auth import authenticate
from datetime import datetime, timedelta
from django.views.decorators.csrf import csrf_exempt

from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny,IsAuthenticated
from rest_framework.decorators import api_view, permission_classes,throttle_classes
from rest_framework.throttling import AnonRateThrottle

from rest_framework_simplejwt.tokens import RefreshToken

from .serializer import UserSerializer
from django.conf import settings



# funtion to refresh both refresh token and acess token
@api_view(['GET'])
@permission_classes([AllowAny])
def get_tokens_for_user(request):
    try:
        user  = request.user
        refresh = RefreshToken.for_user(user)

    except Exception as e:
        return Response({"message":"some thing went wrong"},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    return Response({
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    })

#  funtion to  login a user
@api_view(['POST'])
@permission_classes([AllowAny])
@throttle_classes([AnonRateThrottle])
@csrf_exempt
def login_user(request):
    username = request.data.get('username')
    password = request.data.get('password')

    if not username  or not password:
        message = {}
        if not username:
            message["username"] = "username may not be blank"
        if not password:
            message["password"] = "password may not be blank"

        return Response(message,status=status.HTTP_400_BAD_REQUEST)
    
    user = authenticate(username = username, password = password)
    

    if user is not None:
        refresh = RefreshToken.for_user(user)
        response = Response({
            'refresh': str(refresh),
            'access':str(refresh.access_token)
        })
        print(str(refresh))
        # sends refresh token as httpOnly cookie
        response.set_cookie(
                    key = settings.SIMPLE_JWT['AUTH_COOKIE'], 
                    value = str(refresh),
                    expires = datetime.now()  + settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'],
                    httponly = settings.SIMPLE_JWT['AUTH_COOKIE_HTTP_ONLY'],
                    samesite=settings.SIMPLE_JWT['AUTH_COOKIE_SAMESITE'],  
                    secure=settings.SIMPLE_JWT['AUTH_COOKIE_SECURE'],
            )
        return response


    return Response({"message":"invalid credentials"}, status= status.HTTP_401_UNAUTHORIZED)        


@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
    try:
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        error = serializer.errors
        # this checks if the error is due to existing username
        if 'username' in error:
            for i in error['username']:
                if i.code == "unique":
                    return Response({'message':i},status=status.HTTP_409_CONFLICT)
        # this return works when credentials are not valid
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except :
        return Response({"message":"An unexpected server error occurred. Please try again later."},status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
def is_user_loggedin(request):
    # Access the 'my_cookie' cookie from the request.COOKIES dictionary
    cookie = request.COOKIES.get(settings.SIMPLE_JWT['AUTH_COOKIE'])
    if cookie:
        try:
            refreshToken = RefreshToken(cookie)
            accessToken = str(refreshToken.access_token)
            return Response({'access_token':accessToken},status=status.HTTP_200_OK)
        except Exception as e:
            print('Error : ',e)
            return Response({'details':'invalid token'},status=status.HTTP_401_UNAUTHORIZED)
    else:
        return Response({'details':'invalid token'},status=status.HTTP_401_UNAUTHORIZED) 

# api end point to perform logout (delete refresh token form client by setting its expiration time to past date  )
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_user(request):
    cookie = request.COOKIES.get(settings.SIMPLE_JWT['AUTH_COOKIE'])
    if cookie is None:
        return Response({'detail':'User is already logged out'})
    try:
        refreshToken = RefreshToken(cookie)
        print(refreshToken)
        refreshToken.blacklist()
        response = Response({'detail':'logout successfull'})
        response.set_cookie(
            key = settings.SIMPLE_JWT['AUTH_COOKIE'],
            value='',
            expires=0,
            httponly=True,
            samesite=settings.SIMPLE_JWT['AUTH_COOKIE_SAMESITE'],  
            secure=settings.SIMPLE_JWT['AUTH_COOKIE_SECURE'],        )
        return response
    except Exception as e:
        print("Error : ",e)
        return Response({'detail':'Some thing went wrong'},status=status.HTTP_500_INTERNAL_SERVER_ERROR)