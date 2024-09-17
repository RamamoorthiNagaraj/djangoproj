# views.py
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny,IsAuthenticated
from rest_framework import status
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import UserSerializer, RegisterSerializer,FriendRequestSerializer

from django.db.models import Q
from .models import FriendRequest,CustomUser

User = get_user_model()

@api_view(['POST'])
@permission_classes([AllowAny])
def signup(request):
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        return Response({'message': 'User registered successfully'}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    email = request.data.get('email')
    password = request.data.get('password')
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return Response({'detail': 'Invalid email or password'}, status=status.HTTP_400_BAD_REQUEST)

    if not user.check_password(password):
        return Response({'detail': 'Invalid email or password'}, status=status.HTTP_400_BAD_REQUEST)

    refresh = RefreshToken.for_user(user)
    return Response({
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    })



@api_view(['POST'])
def send_friend_request(request, user_id):
    from_user = request.user
    to_user = User.objects.get(id=user_id)

    if FriendRequest.objects.filter(from_user=from_user, to_user=to_user).exists():
        return Response({'detail': 'Friend request already sent'}, status=status.HTTP_400_BAD_REQUEST)

    FriendRequest.objects.create(from_user=from_user, to_user=to_user)
    return Response({'message': 'Friend request sent'}, status=status.HTTP_201_CREATED)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def search_users(request):
    query = request.query_params.get('query', '')
    if query:
 
        users = User.objects.filter(
            Q(email__iexact=query) | Q(username__icontains=query)
        )[:10]

        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)

    return Response({'detail': 'Query parameter missing'}, status=400)




@api_view(['POST'])
@permission_classes([IsAuthenticated])
def send_friend_request(request):
    to_user_id = request.data.get('to_user')
    to_user = CustomUser.objects.get(id=to_user_id)

    friend_request, created = FriendRequest.objects.get_or_create(
        from_user=request.user, to_user=to_user
    )

    if not created:
        return Response({'detail': 'Friend request already sent or exists.'}, status=400)

    serializer = FriendRequestSerializer(friend_request)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def respond_friend_request(request, request_id):
    try:
        friend_request = FriendRequest.objects.get(id=request_id, to_user=request.user)
    except FriendRequest.DoesNotExist:
        return Response({'detail': 'Friend request not found.'}, status=404)

    action = request.data.get('action')

    if action == 'accept':
        friend_request.status = 'accepted'
    elif action == 'reject':
        friend_request.status = 'rejected'
    else:
        return Response({'detail': 'Invalid action.'}, status=400)

    friend_request.save()

    serializer = FriendRequestSerializer(friend_request)
    return Response(serializer.data)
