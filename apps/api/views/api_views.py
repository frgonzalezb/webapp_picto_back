import os

from django.conf import settings
from django.core.mail import send_mail
from django.http import FileResponse

from rest_framework import exceptions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from ..models import User
from ..serializers import ContactFormSerializer
from ..utils import get_used_storage


class UserStorageView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id, *args, **kwargs):
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist as e:
            print(f'No se ha encontrado al usuario especificado: {e}')
            message = 'No se ha encontrado al usuario especificado.'
            raise exceptions.NotFound(message)
        
        storage_limit = user.storage_limit
        used_storage = get_used_storage(user.id)
        print(f'used_storage = {used_storage}')
        remaining_storage = max(0, storage_limit - used_storage)

        data = {
            'storage_limit': storage_limit,
            'used_storage': used_storage,
            'remaining_storage': remaining_storage
        }

        return Response(data)
    

class ContactFormView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            contact_email = os.environ['CONTACT_EMAIL']

            # Serializar y validar datos del formulario
            serializer = ContactFormSerializer(
                data=request.data, 
                context={"request": request}
            )
            serializer.is_valid(raise_exception=True)

            validated_data = serializer.validated_data

            # Obtener datos del formulario
            nombre = validated_data['nombre']
            email = validated_data['email']
            asunto = validated_data['asunto']
            mensaje = validated_data['mensaje']

            send_mail(
                f'Formulario de contacto, asunto: {asunto}',
                f'Mensaje de: {nombre}\nEmail: {email}\n\nMensaje:\n{mensaje}',
                email,
                [contact_email],
                fail_silently=False,
            )

            return Response(
                {'mensaje': 'Formulario enviado correctamente'}, 
                status=status.HTTP_200_OK
            )
        
        except Exception as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    

class TermsAndConditionsView(APIView):
    def get(self, request):
        try:
            # Ruta al archivo de términos y condiciones
            base_dir = settings.BASE_DIR
            templates_dir = os.path.join(base_dir, 'templates')
            file_path = f'{templates_dir}/policy/terms.txt'

            # Abre y lee el contenido del archivo
            with open(file_path, 'r') as file:
                terms_text = file.read()

            # Devuelve el contenido como una respuesta de archivo
            response = FileResponse(open(file_path, 'rb'))
            response['Content-Disposition'] = 'inline; \
                filename=terminos-y-condiciones.txt'
            
            return response

        except Exception as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
