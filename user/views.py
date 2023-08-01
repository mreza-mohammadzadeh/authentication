from random import randrange

from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from user.models import User, Verify
from user.serializers import UserCreateSerializer, UserListSerializer, UserProfileSerializer
from rest_framework_simplejwt.tokens import RefreshToken


class UserList(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserListSerializer

    def list(self, request, *args, **kwargs):
        # Note the use of `get_queryset()` instead of `self.queryset`
        queryset = self.get_queryset()
        serializer = UserListSerializer(queryset, many=True)
        return Response({"data": serializer.data})


class UserVerify(generics.CreateAPIView):
    authentication_classes = []

    def post(self, request, *args, **kwargs):
        code_random = randrange(111111, 999999)
        verify, response_sms, status_verify = Verify.create_verify(request=request, code=code_random)
        if status_verify == 'sent':
            return Response({"message": "previous_code_is_active"}, status=status.HTTP_200_OK)
        elif status_verify == 'created':
            return Response({"message": "validation_code_sent"}, status=status.HTTP_200_OK)
        else:
            return Response({"message": "error_send_verify_code"}, status=status.HTTP_404_NOT_FOUND)


class UserLogin(generics.CreateAPIView):
    authentication_classes = []

    def post(self, request, *args, **kwargs):
        verify = Verify.check_verify(request)
        if verify == 'notFound':
            return Response({"message": "the_validation_code_is_incorrect"}, status=status.HTTP_404_NOT_FOUND)
        if verify == 'notValid':
            return Response({"message": "the_verification_code_has_expired"}, status=status.HTTP_404_NOT_FOUND)
        try:
            user = User.objects.get(username=request.data['username'])
        except User.DoesNotExist:
            return Response({"message": "you_are_not_registered"}, status=status.HTTP_404_NOT_FOUND)
        user_serializers = UserListSerializer(user)
        token = RefreshToken.for_user(user)
        return Response({
            "message": "you_have_successfully_logged_in", "data": user_serializers.data, "refresh": str(token),
            "access": str(token.access_token)})


class UserRegister(generics.CreateAPIView):
    model = User
    serializer_class = UserCreateSerializer
    authentication_classes = []

    def create(self, request, *args, **kwargs):
        serializer = UserCreateSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token = RefreshToken.for_user(user)
            user_find = User.objects.get(username=request.data['username'])
            serializer_user = UserListSerializer(user_find, many=False)
            return Response(
                {"message": "user_created_successfully", "data": serializer_user.data, "refresh": str(token),
                 "access": str(token.access_token)})
        return Response({"message": "error_in_create_user"}, status=status.HTTP_404_NOT_FOUND)


class UserUpdate(generics.UpdateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = UserProfileSerializer

    def update(self, request, *args, **kwargs):
        instance = User.objects.get(username=self.request.user.username)
        serializer = self.get_serializer(instance, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response({"message": "update_successful", "data": serializer.data})
        else:
            return Response({"message": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class UserGet(generics.ListAPIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        try:
            user = User.objects.get(username=self.request.user.username)
            serializer = UserListSerializer(user, many=False)
            return Response({'data': serializer.data})
        except User.DoesNotExist:
            return Response({'message': 'user_not_found'}, status=status.HTTP_404_NOT_FOUND)
