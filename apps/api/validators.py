import os
import re
import asyncio
import pydnsbl

from django.contrib.auth.password_validation import get_default_password_validators

from rest_framework.exceptions import ValidationError, UnsupportedMediaType, NotFound

from .utils import get_used_storage


class DNSBLVerifier():

    async def verify_email(self, email_address):
        domain = email_address.split('@')[1]
        checker = pydnsbl.DNSBLDomainChecker()
        result = await asyncio.to_thread(checker.check, domain)
        
        return result


async def verify_email_is_blacklisted(value):
    verifier = DNSBLVerifier()
    is_blacklisted = await verifier.verify_email(value)
    
    if '[BLACKLISTED]' in str(is_blacklisted):
        raise ValidationError('Dominio de email en lista negra.')

    return value


def verify_email_complexity(value):
    email_regex = re.compile(r'^[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}$')

    if not email_regex.match(value):
        raise ValidationError('Formato de email inválido.')

    return value


def verify_password_complexity(value):
    password_regex = re.compile(
        r'^(?=.*[a-z])'                 # al menos una minúscula
        r'(?=.*[A-Z])'                  # al menos una mayúscula
        r'(?=.*\d)'                     # al menos un dígito
        r'(?=.*[-_\/@$!%*?&.,:;])'      # al menos un carácter especial
        r'[A-Za-z\d\-_\/@$!%*?&.,:;]'   # caracteres permitidos
    )

    if not password_regex.match(value):
        raise ValidationError('Formato de contraseña inválido.')

    return value


def use_default_password_validators(password):
    validators = get_default_password_validators()
    errors = []

    for validator in validators:
        try:
            validator.validate(password)
        except ValidationError as e:
            errors.extend(e.error_list)

    if errors:
        raise ValidationError(errors)
    
    return password


def verify_file_type(value, content_type):
    if value:
        if content_type == 'Pictograma' or content_type == 'Rutina':
            if value.content_type not in ['image/png', 'image/jpg', 'image/jpeg']:
                raise UnsupportedMediaType('Formato de archivo no válido.')
        elif content_type == 'Audio':
            if value.content_type not in ['audio/mpeg', 'audio/wav']:
                raise UnsupportedMediaType('Formato de archivo no válido.')
    
    return value


def verify_file_size(value, user):
    if value.size > 1024 * 1024:  # 1 MB
        msg = 'Tamaño de archivo demasiado grande.'
        raise ValidationError(msg)
    
    verify_remaining_storage_for_file(value, user)
    
    return value


def verify_remaining_storage_for_file(value, user):
    storage_limit = user.storage_limit
    used_storage = get_used_storage(user.id)
    remaining_storage = max(0, storage_limit - used_storage)

    if remaining_storage <= 0 or value.size >= remaining_storage:
        msg = 'No hay espacio suficiente para almacenar este archivo.'
        raise ValidationError(msg)
    
    return value


def verify_content_name(value):
    allowed_chars = re.compile('^[A-Za-z0-9áéíóúÁÉÍÓÚüÜñÑ¿?¡!()+\\-*/=#$%., ]+$')

    if not allowed_chars.match(value):
        msg = 'El campo nombre contiene caracteres no permitidos.'
        raise ValidationError()
    
    if value.isspace():
        msg = 'El nombre no puede contener solo espacios.'
        raise ValidationError(msg)
    
    if len(value) > 50 or len(value) < 1:
        msg = 'El nombre debe tener entre 1 y 50 caracteres.'
        raise ValidationError(msg)
    
    return value


def verify_file_path(file_path):
    if not os.path.exists(file_path):
        raise NotFound("Archivo no encontrado o ruta errónea.")
    

def check_min_max_length(value, min_size, max_size):
    if len(str(value)) < min_size or len(str(value)) > max_size:
        msg = 'El valor no se ajusta al largo establecido.'
        raise ValidationError(msg)


def verify_value_length(value, min_size, max_size, is_optional_field):
    if is_optional_field:
        if value or value != '':
            check_min_max_length(value, min_size, max_size)
    else:
        check_min_max_length(value, min_size, max_size)
    
    return value


def check_name_complexity(value):
    pattern = re.compile(r'^[a-zA-ZáéíóúÁÉÍÓÚüÜñÑ\s]+$')

    if not pattern.match(value):
        msg = 'Sólo se aceptan letras y espacios para este campo.'
        raise ValidationError(msg)

    return value


def verify_name_complexity(value, is_optional_field):
    if is_optional_field:
        if value or value != '':
            check_name_complexity(value)
    else:
        check_name_complexity(value)
    
    return value
