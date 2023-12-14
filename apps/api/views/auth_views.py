from django.contrib.auth import authenticate
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from apps.api.models import AccountActivationToken
from apps.api.serializers import UserSerializer


class LoginView(TokenObtainPairView):
    serializer_class = TokenObtainPairSerializer

    def post(self, request, *args, **kwargs):

        # Captura las credenciales de la petición
        login_serializer = self.serializer_class(
            data=request.data, 
            context={'request': request}
        )

        # Verifica que los campos no sean nulos ni estén en blanco
        if not login_serializer.is_valid():
            return Response(
                {'error': 'No se han ingresado las credenciales válidas.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        # Intenta autenticar al usuario
        user = authenticate(
            email=request.data['email'],
            password=request.data['password']
        )

        # Si el usuario no existe...
        if not user:
            return Response(
                {'error': 'El usuario no existe.'}, 
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        # Si el usuario no está activo...
        if not user.is_active:
            return Response(
                {'error': 'El usuario no está activo.'},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        # Serializa la información del usuario
        user_serializer = UserSerializer(user)

        # Genera la respuesta
        return Response(
            {
                'token': login_serializer.validated_data.get('access'),
                'refresh_token': login_serializer.validated_data.get('refresh'),
                'user': user_serializer.data,
            },
            status= status.HTTP_200_OK,
        )
        
    
class LogoutView(GenericAPIView):

    def post(self, request, *args, **kwargs):
        user = request.user

        if not user:
            return Response(
                {'error': 'El usuario no existe.'}, 
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        RefreshToken.for_user(user)
        
        return Response(
            {'mensaje':'La sesión ha sido cerrada con éxito.'}, 
            status=status.HTTP_200_OK,
        )
    

class AccountActivationView(APIView):
    def get(self, request, token):
        try:
            token_obj = AccountActivationToken.objects.get(token=token)

            user = token_obj.user
            user.is_active = True

            user.save()
            token_obj.delete()

            return Response(
                {'message': 'Your account has been activated successfully.'}
            )
        
        except ObjectDoesNotExist:
            return Response({'error': 'Invalid activation token.'})


class AccountDeactivationView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = request.user

        if user.is_active:
            user.is_active = False
            user.inactive_since = timezone.now()
            user.save()

            return Response(
                {'message': 'Cuenta desactivada exitosamente.'}, 
                status=status.HTTP_200_OK
            )

        else:
            return Response(
                {'message': 'La cuenta ya está desactivada.'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
