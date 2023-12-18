"""
Utilidades varias, separadas para una mejor lectura y debugging del código.
"""

import os
import re
import json

from datetime import datetime

from django.conf import settings

from rest_framework import exceptions


def get_queryset_by_user_type(model, request):
    """
    Se permite que si la instancia de usuario:

    - Es staff, solo pueda acceder al contenido precargado.
    - De lo contrario, puede acceder al contenido precargado y propio.
    """
    user = request.user
    model_verbose_name = model._meta.verbose_name

    try:
        if model_verbose_name == 'Rutina':
            queryset = model.objects.filter(autor=user.id)

        else:
            if user.is_staff:
                queryset = model.objects.filter(es_precargado=True)
            
            else:
                preloaded_content = model.objects.filter(es_precargado=True)
                user_content = model.objects.filter(autor=user.id)
                queryset = preloaded_content | user_content
        
        return queryset

    except:
        raise exceptions.PermissionDenied('Acceso denegado.')
    

def get_used_storage(user_id):
    '''
    Devuelve el almacenamiento de cada usuario en bytes.
    '''
    media_root = settings.MEDIA_ROOT
    user_folder = f'user_content/{user_id}/'
    storage_path = os.path.join(media_root, user_folder)
    print(f'storage_path = {storage_path}')
    total_size = 0

    try:
        for dirpath, dirnames, filenames in os.walk(storage_path):
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                total_size += os.path.getsize(filepath)

        return total_size
    
    except OSError as e:
        print(f"Error en get_used_storage(): {e.strerror}")
        raise exceptions.ValidationError('Error en el servidor.')


def get_user_instance(user_id, user_model):
    try:
        user = user_model.objects.get(pk=user_id)
    except user_model.DoesNotExist:
        raise exceptions.NotFound('Usuario no encontrado.')

    if not user.is_active:
        raise exceptions.ValidationError('Usuario inactivo.')
    
    return user


def filename_generator(name, file):
    """
    Retorna un nombre de archivo con el siguiente formato (sn comillas):

    "{timestamp}_{nombre_del_contenido}.{extension}"

    Utiliza una expresión regular para reemplazar los caracteres no deseados 
    por guiones bajos.
    """
    try:
        clean_name = re.sub(r'[\\/:*?"<>|\s]', '_', name)
        _, extension = os.path.splitext(file.name)
        right_now = datetime.now()
        timestamp = str(datetime.timestamp(right_now)).replace('.', '-')
        new_filename = f'{timestamp}_{clean_name}{extension}'

        return new_filename
    
    except OSError as e:
        print(f"Error en filename_generator(): {e.strerror}") # debug
        raise exceptions.ValidationError('Error en el servidor.')


def path_generator(user_instance, content_type, filename):
    """
    Retorna una ruta para almacenar el contenido, 
    según si el usuario sea staff o común.
    """
    try:
        user_id = user_instance.id
        root = settings.MEDIA_ROOT

        if user_instance.is_staff:
            path = os.path.join(
                root, 
                'preloaded',
                content_type, 
                filename
            )
        else:
            path = os.path.join(
                root, 
                'user_content', 
                str(user_id), 
                content_type, 
                filename
            )

        # Verifica y crea los directorios necesarios
        dir = os.path.dirname(path)
        os.makedirs(dir, exist_ok=True)

        return path
    
    except OSError as e:
        print(f"Error en path_generator(): {e.strerror}") # debug
        raise exceptions.ValidationError('Error en el servidor.')


def create_content_instance(
        user_instance, 
        content_model, 
        content_name, 
        relative_path,
    ):
    """
    Crea y retorna la instancia del contenido en la base de datos.

    NOTA: Sólo genera la instancia (fila de la tabla en la base de datos).
    El almacenamiento del contenido como tal es realizado por otras funciones.
    Esta es una función auxiliar dentro de todo el proceso.
    """
    if user_instance.is_staff:
        content = content_model.objects.create(
            nombre=content_name,
            ruta=relative_path,
            autor=user_instance,
            es_precargado=True
        )
    else:
        content = content_model.objects.create(
            nombre=content_name,
            ruta=relative_path,
            autor=user_instance
        )

    return content


def create_content(content_model, user_model, content_folder, validated_data):
    """
    Función matriz que genera el contenido (pictograma o sonido)
    en el sistema. Utiliza funciones auxiliares ad hoc.

    Parámetros:
    - model_class = La clase del modelo del contenido (e.g. Pictograma)
    - user_model = La clase del modelo de usuario (e.g. Usuario)
    - content_folder = La carpeta para el contenido (e.g. 'pictogramas')
    - validated_data = (autoexplicatorio)
    """
    try:
        user_id = validated_data['autor']
        content_name = validated_data['nombre']
        content_file = validated_data['ruta']

        # Obtener la instancia de usuario
        user = get_user_instance(user_id, user_model)
        
        # Guarda el archivo
        file = save_file(user, content_name, content_file, content_folder)
        
        # Establece la ruta relativa a guardar en la instancia
        relative_path = os.path.relpath(file, settings.MEDIA_ROOT)

        # Crea y devuelve la instancia
        content_instance = create_content_instance(
            user_instance=user,
            content_model=content_model,
            content_name=content_name,
            relative_path=relative_path
        )

        return content_instance
    
    except OSError as e:
        print(f"Error en create_content(): {e.strerror}") # debug
        raise exceptions.ValidationError('Error en el servidor.')


def remove_instance_file(instance):
    try:
        file = instance.ruta
        file_path = file.path

        if not os.path.exists(file_path):
            raise exceptions.NotFound("Archivo no encontrado o ruta errónea.")
        
        file.close()
        
        os.remove(file_path)

    except OSError as e:
        print(f"Error en remove_instance_file(): {e.strerror}") # debug
        raise exceptions.ValidationError('Error en el servidor.')


def save_file(user, name, file, content_folder):
    try:
        filename = filename_generator(name, file)

        file_path = path_generator(
            user_instance=user, 
            content_type=content_folder, 
            filename=filename
        )

        with open(file_path, 'wb') as f:
            f.write(file.read())

        return file_path
    except OSError as e:
        print(f"Error en save_file(): {e.strerror}") # debug
        raise exceptions.ValidationError('Error en el servidor.')


def rename_file(instance, new_name):
    try:
        instance.ruta.close()

        old_path = instance.ruta.path
        _, extension = os.path.splitext(old_path)
        
        new_filename = filename_generator(new_name, instance.ruta)
        new_path = os.path.join(os.path.dirname(old_path), new_filename)

        os.rename(old_path, new_path)

        relative_path = os.path.relpath(new_path, settings.MEDIA_ROOT)

        return relative_path

    except OSError as e:
        print(f"Error en rename_file(): {e.strerror}") # debug
        raise exceptions.ValidationError('Error en el servidor.')


def update_content(
        user_model, 
        content_folder, 
        instance, 
        validated_data
    ):
    """
    Función matriz que actualiza el contenido (pictograma o sonido)
    en el sistema. Utiliza funciones auxiliares ad hoc.

    Parámetros:
    - user_model = La clase del modelo de usuario (e.g. Usuario)
    - content_folder = La carpeta del contenido (e.g. 'pictogramas')
    - instance = La instancia ya existente del contenido
    - validated_data = Los nuevos datos para la instancia
    """
    try:
        user_id = validated_data['autor'].id

        new_content_name = validated_data['nombre']
        new_content_file = validated_data['ruta']

        old_content_name = instance.nombre
        old_content_file = instance.ruta

        # Obtener la instancia de usuario
        user = get_user_instance(user_id=user_id, user_model=user_model)

        '''
        Opciones:
        1. Si en el request hay nuevo archivo (pero se mantiene nombre)
        2. Si en el request hay nuevo nombre (pero se mantiene archivo)
        3. Si el el request hay ambos nuevos
        4. Si no hay cambio alguno
        '''

        # 1
        if new_content_file != old_content_file and \
        new_content_name == old_content_name:
            print('--update_content: option #1') # debug
            remove_instance_file(instance)
            
            new_file = save_file(
                user, 
                old_content_name, 
                new_content_file, 
                content_folder
            )
            
            relative_path = os.path.relpath(new_file, settings.MEDIA_ROOT)
            instance.ruta = relative_path
            instance.save()
        
        # 2
        elif new_content_name != old_content_name and \
        new_content_file == old_content_file:
            print('--update_content: option #2') # debug
            new_name_and_path = rename_file(instance, new_content_name)

            instance.nombre = new_content_name
            instance.ruta = new_name_and_path
            instance.save()
        
        #3
        elif new_content_file != old_content_file and \
        new_content_name != old_content_name:
            print('--update_content: option #3') # debug
            remove_instance_file(instance)
            
            new_file = save_file(
                user, 
                new_content_name, 
                new_content_file, 
                content_folder
            )
            
            relative_path = os.path.relpath(new_file, settings.MEDIA_ROOT)
            instance.nombre = new_content_name
            instance.ruta = relative_path
            instance.save()
        
        #4
        else:
            print('No se han realizado cambios al contenido.') # debug
            pass

        return instance
    
    except OSError as e:
        print(f"Error en update_content(): {e.strerror}") # debug
        raise exceptions.ValidationError('Error en el servidor.')


# ------------------------------------------------------------------------------
# Utilidades especiales para el modelo Rutina
# ------------------------------------------------------------------------------

def json_filename_generator(content_name):
    try:
        clean_name = re.sub(r'[\\/:*?"<>|\s]', '_', content_name)
        right_now = datetime.now()
        timestamp = str(datetime.timestamp(right_now)).replace('.', '-')
        new_filename = f'{timestamp}_{clean_name}.json'

        return new_filename
    
    except OSError as e:
        print(f"Error en json_filename_generator(): {e.strerror}") # debug
        raise exceptions.ValidationError('Error en el servidor.')


def create_json_file(user_instance, content_name, content_json):
    try:
        filename = json_filename_generator(content_name)

        file_path = path_generator(
            user_instance=user_instance, 
            content_type='routines', 
            filename=filename
        )

        with open(file_path, 'w') as file:
            json.dump(content_json, file, indent=4)

        # Establece la ruta relativa a guardar en la instancia
        relative_path = os.path.relpath(file_path, settings.MEDIA_ROOT)

        return relative_path
    
    except OSError as e:
        print(f"Error en create_json_file(): {e.strerror}") # debug
        raise exceptions.ValidationError('Error en el servidor.')


def rename_json_file(instance, new_name):
    rel_path = instance.json_rutina

    if not rel_path or rel_path == '':
        raise exceptions.NotFound('Archivo no encontrado.')
    
    else:
        try:
            old_path = os.path.join(settings.MEDIA_ROOT + '/' + rel_path)

            if os.path.exists(old_path):
                rel_path.close()
                _, extension = os.path.splitext(old_path)

            new_filename = json_filename_generator(new_name)
            new_path = os.path.join(os.path.dirname(old_path), new_filename)

            os.rename(old_path, new_path)

            new_relative_path = os.path.relpath(new_path, settings.MEDIA_ROOT)

            return new_relative_path
    
        except OSError as e:
            print(f"Error en rename_json_file(): {e}")
            raise exceptions.ValidationError('Error en el servidor.')


def remove_json_file(instance):
    try:
        rel_path = instance.json_rutina
        abs_path = os.path.join(settings.MEDIA_ROOT + '/' + rel_path)

        if os.path.exists(abs_path):
            os.remove(abs_path)
        else:
            raise exceptions.NotFound(f"El archivo {abs_path} no existe.")
        
    except OSError as e:
        print(f"Error en remove_json_file(): {e}")
        raise exceptions.ValidationError('Error en el servidor.')


def rename_cover_file(instance, new_name):
    try:
        instance.url_portada.close()

        old_path = instance.url_portada.path
        _, extension = os.path.splitext(old_path)

        new_filename = filename_generator(new_name, instance.url_portada)
        new_path = os.path.join(os.path.dirname(old_path), new_filename)

        os.rename(old_path, new_path)

        new_relative_path = os.path.relpath(new_path, settings.MEDIA_ROOT)

        return new_relative_path
    
    except OSError as e:
        print(f"Error en rename_cover_file(): {e}")
        raise exceptions.ValidationError('Error en el servidor.')


def remove_cover_file(instance):
    try:
        file = instance.url_portada
        
        if not file or file == '':
            pass

        else:
            file_path = file.path

            if not os.path.exists(file_path):
                raise exceptions.NotFound(
                    'Archivo no encontrado o ruta errónea.'
                )
            
            file.close()

            os.remove(file_path)

    except OSError as e:
        print(f"Error en remove_cover_file(): {e}")
        raise exceptions.ValidationError('Error en el servidor.')


def create_routine_instance(
        user_instance, 
        content_model, 
        content_name, 
        relative_path,
        json_file_path
    ):
    """
    Crea y retorna la instancia del contenido Rutina en la base de datos.

    NOTA: Sólo genera la instancia (fila de la tabla en la base de datos).
    El almacenamiento del contenido como tal es realizado por otras funciones.
    Esta es una función auxiliar dentro de todo el proceso.
    """
    content = content_model.objects.create(
        nombre=content_name,
        json_rutina=json_file_path,
        url_portada=relative_path,
        autor=user_instance
    )

    return content


def create_routine(content_model, user_model, content_folder, validated_data):
    """
    Función matriz que genera el contenido especialmente para el modelo Rutina
    en el sistema. Utiliza funciones auxiliares ad hoc.

    Parámetros:
    - content_model = La clase del modelo del contenido (e.g. Rutina)
    - user_model = La clase del modelo de usuario (e.g. Usuario)
    - content_folder = La carpeta para el contenido (e.g. 'covers')
    - validated_data = (autoexplicatorio)
    """
    try:
        user_id = validated_data['autor']
        content_name = validated_data['nombre']
        content_file = validated_data['url_portada']
        content_json = validated_data['json_rutina']

        # Obtener la instancia de usuario y crear el archivo JSON de la rutina
        user = get_user_instance(user_id, user_model)
        base_file = create_json_file(user, content_name, content_json)
        
        if content_file:
            # Guarda el archivo
            file = save_file(user, content_name, content_file, content_folder)
            
            # Establece la ruta relativa a guardar en la instancia
            relative_path = os.path.relpath(file, settings.MEDIA_ROOT)
        else:
            relative_path = None

        # Crea y devuelve la instancia
        content_instance = create_routine_instance(
            user_instance=user,
            content_model=content_model,
            content_name=content_name,
            relative_path=relative_path,
            json_file_path=base_file
        )

        return content_instance
    
    except OSError as e:
        print(f"Error en create_routine(): {e}")
        raise exceptions.ValidationError('Error en el servidor.')


def update_routine_instance(
        content_model,
        user_model, 
        content_folder, 
        instance, 
        validated_data
    ):
    """
    Función matriz especial que actualiza el contenido de tipo Rutina
    en el sistema. Utiliza funciones auxiliares ad hoc.

    Parámetros:
    - content_model = La clase del modelo del contenido (e.g. Rutina)
    - user_model = La clase del modelo de usuario (e.g. Usuario)
    - content_folder = La carpeta del contenido como cadena (e.g. 'pictogramas')
    - instance = La instancia ya existente del contenido
    - validated_data = Los nuevos datos para la instancia
    """
    try:
        user_id = validated_data['autor'].id
        
        new_content_name = validated_data['nombre']
        new_content_file = validated_data['url_portada']
        new_content_json = validated_data['json_rutina']

        old_content_name = instance.nombre
        old_content_file = instance.url_portada
        old_content_json = instance.json_rutina

        if old_content_file == '':
            old_content_file = None

        user = get_user_instance(user_id=user_id, user_model=user_model)

        '''
        Opciones:
        1. Si en el request hay nuevo archivo (pero se mantiene nombre y json)
        2. Si en el request hay nuevo nombre (pero se mantiene archivo y json)
        3. Si en el request hay nuevo json (pero se mantiene archivo y nombre)
        4. Si en el request hay nuevo archivo y nombre (pero se mantiene json)
        5. Si en el request hay nuevo archivo y json (pero se mantiene nombre)
        6. Si en el request hay nuevo nombre y json (pero se mantiene archivo)
        7. Si en el request hay nuevo nombre, json y archivo
        8. Si no hay cambio alguno
        '''

        # 1
        if new_content_file != old_content_file and \
        new_content_name == old_content_name and \
        new_content_json == old_content_json:
            print('--update_rutina_instance: option #1') # debug

            remove_cover_file(instance)
            new_file = save_file(
                user, 
                old_content_name, 
                new_content_file, 
                content_folder
            )
            
            new_relative_path = os.path.relpath(new_file, settings.MEDIA_ROOT)

            instance.url_portada = new_relative_path
            instance.save()
        
        # 2
        elif new_content_name != old_content_name and \
        new_content_file == old_content_file and \
        new_content_json == old_content_json:
            print('--update_rutina_instance: option #2') # debug

            new_json_filename = rename_json_file(instance, new_content_name)

            new_cover_filename = rename_file(
                instance, 
                new_content_name, 
                content_model
            )

            instance.nombre = new_content_name
            instance.json_rutina = new_json_filename
            instance.url_portada = new_cover_filename
            instance.save()

        # 3
        elif new_content_json != old_content_json and \
        new_content_file == old_content_file and \
        new_content_name == old_content_name:
            print('--update_rutina_instance: option #3') # debug
            
            remove_json_file(instance)
            new_json_file = create_json_file(
                user_instance=user,
                content_name=old_content_name,
                content_json=new_content_json
            )

            instance.json_rutina = new_json_file
            instance.save()

        # 4
        elif new_content_file != old_content_file and \
        new_content_name != old_content_name and \
        new_content_json == old_content_json:
            print('--update_rutina_instance: option #4') # debug

            new_json_filename = rename_json_file(instance, new_content_name)

            remove_cover_file(instance)
            new_file = save_file(
                user, 
                new_content_name, 
                new_content_file, 
                content_folder
            )
            
            new_relative_path = os.path.relpath(new_file, settings.MEDIA_ROOT)

            instance.nombre = new_content_name
            instance.json_rutina = new_json_filename
            instance.url_portada = new_relative_path
            instance.save()

        # 5
        elif new_content_file != old_content_file and \
        new_content_json != old_content_json and \
        new_content_name == old_content_name:
            print('--update_rutina_instance: option #5') # debug

            remove_json_file(instance)
            new_json_file = create_json_file(
                user_instance=user,
                content_name=old_content_name,
                content_json=new_content_json
            )

            remove_cover_file(instance)
            new_file = save_file(
                user, 
                old_content_name, 
                new_content_file, 
                content_folder
            )
            
            new_relative_path = os.path.relpath(new_file, settings.MEDIA_ROOT)

            instance.json_rutina = new_json_file
            instance.url_portada = new_relative_path
            instance.save()

        # 6
        elif new_content_name != old_content_name and \
        new_content_json != old_content_json and \
        new_content_file == old_content_file:
            print('--update_rutina_instance: option #6') # debug

            remove_json_file(instance)
            new_json_file = create_json_file(
                user_instance=user,
                content_name=new_content_name,
                content_json=new_content_json
            )

            new_cover_filename = rename_file(
                instance, 
                new_content_name, 
                content_model
            )

            instance.nombre = new_content_name
            instance.json_rutina = new_json_file
            instance.url_portada = new_cover_filename
            instance.save()

        # 7
        elif new_content_name != old_content_name and \
        new_content_json != old_content_json and \
        new_content_file != old_content_file:
            print('--update_rutina_instance: option #7') # debug

            remove_json_file(instance)
            new_json_file = create_json_file(
                user_instance=user,
                content_name=new_content_name,
                content_json=new_content_json
            )

            remove_cover_file(instance)
            new_file = save_file(
                user, 
                new_content_name, 
                new_content_file, 
                content_folder
            )
            
            new_relative_path = os.path.relpath(new_file, settings.MEDIA_ROOT)

            instance.nombre = new_content_name
            instance.url_portada = new_relative_path
            instance.json_rutina = new_json_file
            instance.save()
        
        # 8
        else:
            print('No se han realizado cambios al contenido.') # debug
            pass

        return instance
        
    except OSError as e:
        print(f"Error en update_content(): {e.strerror}") # debug
        raise exceptions.ValidationError('Error en el servidor.')
