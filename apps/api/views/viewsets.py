import os
import json

from rest_framework import exceptions, status, viewsets
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.response import Response

from rest_framework_simplejwt.authentication import JWTAuthentication

from apps.api.serializers import UserSerializer
from apps.api.serializers import PictogramaSerializer
from apps.api.serializers import AudioSerializer
from apps.api.serializers import RutinaSerializer

from apps.api.utils import get_queryset_by_user_type
from apps.api.utils import remove_instance_file
from apps.api.utils import remove_cover_file
from apps.api.utils import remove_json_file


# ----- User -----
class UserViewSet(viewsets.ModelViewSet):
    authentication_classes = [JWTAuthentication]
    serializer_class = UserSerializer
    model = serializer_class.Meta.model
    queryset = model.objects.all()

    def get_permissions(self):
        if self.action == 'create':
            # Permite a cualquiera registrar (crear) un usuario
            return [AllowAny()]
        elif self.action == 'list':
            # Sólo los administradores pueden listar usuarios
            return [IsAdminUser()]
        else:
            # Requiere que el usuario esté autenticado para todo lo demás
            return [IsAuthenticated()]
    
    def create(self, request, *args, **kwargs):
        if not request.data:
            raise exceptions.NotFound('No hay datos en la petición.')

        serializer = self.get_serializer(
            data=request.data, 
            context={'request': request}
        )

        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        
        return Response(
            serializer.data, 
            status=status.HTTP_201_CREATED, 
            headers=headers,
        )
    
    def update(self, request, *args, **kwargs):
        if not request.data:
            raise exceptions.NotFound('No hay datos en la petición.')
        
        if not self.request.user or not request.user.is_staff:
            msg = 'Sólo el mismo usuario o un administrador pueden \
                editar una cuenta de usuario.'
            raise exceptions.PermissionDenied(msg)
        
        instance = self.get_object()
        serializer = self.get_serializer(
            instance, 
            data=request.data, 
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response(serializer.data, status=status.HTTP_200_OK)


# ----- Pictograma ----- OK
class PictogramaViewSet(viewsets.ModelViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = PictogramaSerializer
    parser_classes = (MultiPartParser, FormParser)
    model = serializer_class.Meta.model

    # ----- get_queryset ----- OK
    def get_queryset(self):
        queryset = get_queryset_by_user_type(
            model=self.model, 
            request=self.request
        )

        return queryset
    
    # ----- list ----- OK
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        
        return Response(
            serializer.data, 
            status=status.HTTP_200_OK,
        )
    
    # ----- perform_create ----- OK
    def perform_create(self, serializer):
        serializer.save(autor=self.request.user.id)
    
    # ----- create ----- OK
    def create(self, request, *args, **kwargs):
        if not request.data:
            raise exceptions.NotFound('No hay datos en la petición.')
        
        data = {
            'nombre': request.data.get('name'), 
            'ruta': request.data.get('file'), 
            'autor': self.request.user.id, 
        }
        serializer = self.serializer_class(data=data)
        serializer.is_valid(raise_exception=True)

        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)

        return Response(
            serializer.data, 
            status=status.HTTP_201_CREATED, 
            headers=headers,
        )
    
    # ----- retrieve ----- OK
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )

    # ----- update ----- OK
    def update(self, request, *args, **kwargs):
        if not request.data:
            raise exceptions.NotFound('No hay datos en la petición.')
        
        instance = self.get_object()

        new_name = request.data.get('name')
        new_path = request.data.get('file')
        old_name = instance.nombre
        old_path = instance.ruta

        data = {
            'nombre': new_name if new_name else old_name,
            'ruta': new_path if new_path else old_path,
            'autor': self.request.user.id
        }

        if data['nombre'] == old_name and data['ruta'] == old_path:
            msg = {'message': 'No changes found in the request.'}
            
            return Response(msg, status=status.HTTP_200_OK)

        serializer = self.serializer_class(
            instance=instance,
            data=data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response(serializer.data, status=status.HTTP_200_OK)
    
    # ----- destroy ----- OK
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        remove_instance_file(instance)
        instance.delete()

        msg = {'message': 'Content deleted successfully.'}

        return Response(msg, status=status.HTTP_200_OK)
            
            
# ----- Audio -----
class AudioViewSet(viewsets.ModelViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = AudioSerializer
    parser_classes = (MultiPartParser, FormParser)
    model = serializer_class.Meta.model

    # ----- get_queryset ----- OK
    def get_queryset(self):
        queryset = get_queryset_by_user_type(
            model=self.model, 
            request=self.request
        )

        return queryset
    
    # ----- list ----- OK
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    # ----- perform_create ----- OK
    def perform_create(self, serializer):
        serializer.save(autor=self.request.user.id)

    # ----- create ----- OK
    def create(self, request, *args, **kwargs):
        if not request.data:
            raise exceptions.NotFound('No hay datos en la petición.')
        
        data = {
            'nombre': request.data.get('name'), 
            'ruta': request.data.get('file'), 
            'autor': self.request.user.id
        }
        serializer = self.serializer_class(data=data)
        serializer.is_valid(raise_exception=True)

        self.perform_create(serializer)

        headers = self.get_success_headers(serializer.data)
        status_code = status.HTTP_201_CREATED

        return Response(serializer.data, status=status_code, headers=headers)
    
    # ----- retrieve ----- OK
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )
    
    # ----- update ----- OK
    def update(self, request, *args, **kwargs):
        if not request.data:
            raise exceptions.NotFound('No hay datos en la petición.')
        
        instance = self.get_object()

        new_name = request.data.get('name')
        new_path = request.data.get('file')
        old_name = instance.nombre
        old_path = instance.ruta

        data = {
            'nombre': new_name if new_name else old_name,
            'ruta': new_path if new_path else old_path,
            'autor': self.request.user.id
        }

        if data['nombre'] == old_name and data['ruta'] == old_path:
            msg = {'message': 'No changes found in the request.'}
            
            return Response(msg, status=status.HTTP_200_OK)

        serializer = self.serializer_class(
            instance=instance,
            data=data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response(serializer.data, status=status.HTTP_200_OK)
    
    # ----- destroy ----- OK
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        remove_instance_file(instance)
        instance.delete()

        msg = {'message': 'Content deleted successfully.'}
        
        return Response(msg, status=status.HTTP_200_OK)
    

# ----- Rutina -----
class RutinaViewSet(viewsets.ModelViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = RutinaSerializer
    parser_classes = (MultiPartParser, FormParser)
    model = serializer_class.Meta.model

    # ----- get_queryset ----- OK
    def get_queryset(self):
        queryset = get_queryset_by_user_type(
            model=self.model, 
            request=self.request
        )

        return queryset
    
    # ----- perform_create ----- OK
    def perform_create(self, serializer):
        serializer.save(autor=self.request.user.id)
    
    # ----- create ----- OK
    def create(self, request, *args, **kwargs):
        if not request.data:
            raise exceptions.NotFound('No hay datos en la petición.')
        
        name = request.data.get('name')
        cover = request.data.get('file')
        json = request.data.get('json')

        data = {
            'nombre': name, 
            'json_rutina': json,
            'url_portada': cover if cover else None, 
            'autor': self.request.user.id
        }
        serializer = self.serializer_class(data=data)
        serializer.is_valid(raise_exception=True)

        self.perform_create(serializer)

        headers = self.get_success_headers(serializer.data)
        status_code = status.HTTP_201_CREATED

        return Response(serializer.data, status=status_code, headers=headers)
    
    # ----- retrieve ----- OK
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()

        json_file_path = os.path.join('media', instance.json_rutina)

        with open(json_file_path, 'r') as json_file:
            json_content = json.load(json_file)

        serializer = self.get_serializer(instance)
        response_data = serializer.data
        response_data['json_rutina'] = json_content

        return Response(response_data, status=status.HTTP_200_OK)
    
    # ----- update -----
    def update(self, request, *args, **kwargs):
        if not request.data:
            raise exceptions.NotFound('No hay datos en la petición.')
        
        instance = self.get_object()

        new_name = request.data.get('name')
        new_file = request.data.get('file')
        new_json = request.data.get('json')
        old_name = instance.nombre
        old_file = instance.url_portada

        if old_file == '':
            old_file = None

        if new_name == old_name and new_file == old_file:
            print('No se han registrado cambios')
            return Response(
                {'No se han registrado cambios'}, 
                status.HTTP_200_OK
            )

        data = {
            'nombre': new_name if new_name else old_name, 
            'json_rutina': new_json,
            'url_portada': new_file if new_file else old_file,
            'autor': self.request.user.id
        }

        serializer = self.serializer_class(
            instance=instance,
            data=data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response(serializer.data, status=status.HTTP_200_OK)
    
    # ----- destroy -----
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        remove_json_file(instance)
        remove_cover_file(instance)
        instance.delete()

        msg = {'message': 'Content deleted successfully.'}
        
        return Response(msg, status=status.HTTP_200_OK)
