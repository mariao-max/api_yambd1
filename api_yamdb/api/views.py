from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404, render
from rest_framework import status, viewsets
from rest_framework.decorators import action, api_view
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from .permissions import UserIsAdmin, UserIsAdminOrReadOnly, UserIsModerator
from .serializers import AuthSerializer, UserSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (UserIsAdmin,)
    lookup_field = 'username'
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username',)

    @action(
        detail=False,
        methods=['get', 'post'],
        url_path='me',
        permission_classes=(IsAuthenticated,),
    )
    def set_profile(self, request, pk=None):
        user = get_object_or_404(User, pk=request.user.id)
        serializer = self.get_serializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

@action(
    detail=False,
    methods=['post'],
    permission_classes=(AllowAny,)
)
def sign_up(requset):
    serializers = AuthSerializer(data=requset.data)
    serializers.is_valid(raise_exception=True)
    email = serializers.validated_data['email']
    username = serializers.validated_data['username']
    confirmation_code = default_token_generator.make_token(username)
    user, created = User.objects.get_or_create(
        **serializers.validated_data,
        confirmation_code=confirmation_code
    )
    send_mail(
        'Код для доступа к токену',
        f'{user.confirmation_code}',
        'admin@yamdb.com',
        [f'{email}'],
    )
    return Response(serializers.data, status=status.HTTP_200_OK)

@action(
    detail=False,
    methods=['post'],
    permission_classes=(AllowAny,)
)
def get_token_for_user(requset):
    serializers = AuthSerializer(data=requset.data)
    serializers.is_valid(raise_exception=True)
    username = serializers.validated_data['username']
    confirmation_code = serializers.validated_data['confirmation_code']
    user = get_object_or_404(User, username=username)
    if confirmation_code != user.confirmation_code:
        return Response(status=status.HTTP_400_BAD_REQUEST)
    token = RefreshToken.for_user(user)
    return Response(
        {'token': str(refresh.access_token)},
        status=status.HTTP_200_OK
    )
