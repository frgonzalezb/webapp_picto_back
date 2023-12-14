import re

from django.utils.translation import gettext_lazy as _

from rest_framework import serializers
from drf_recaptcha.fields import ReCaptchaV2Field

from .models import User, Pictograma, Audio, Rutina

from .utils import create_content
from .utils import update_content
from .utils import create_routine
from .utils import update_routine_instance
from .utils import get_user_instance

from .validators import verify_email_complexity
from .validators import verify_email_is_blacklisted
from .validators import verify_password_complexity
from .validators import use_default_password_validators
from .validators import verify_file_type
from .validators import verify_file_size
from .validators import verify_content_name
from .validators import verify_value_length
from .validators import verify_name_complexity


class ContactFormSerializer(serializers.Serializer):
    nombre = serializers.CharField()
    email = serializers.EmailField()
    asunto = serializers.CharField()
    mensaje = serializers.CharField()
    recaptcha = ReCaptchaV2Field()

    def get_fields(self):
        fields = super().get_fields()
        fields.update({'recaptcha': ReCaptchaV2Field()})
        
        return fields
    
    def validate(self, attrs):
        attrs.pop("recaptcha")
        
        return attrs
    
    def validate_nombre(self, value):
        verify_value_length(
            value=value, 
            min_size=2, 
            max_size=50, 
            is_optional_field=True
        )
        verify_name_complexity(value, True)

        return value
        
    def validate_email(self, value):
        verify_value_length(
            value=value, 
            min_size=6, 
            max_size=250, 
            is_optional_field=False
        )
        verify_email_complexity(value)
        verify_email_is_blacklisted(value)

        return value
    
    def validate_asunto(self, value):
        verify_value_length(
            value=value, 
            min_size=2, 
            max_size=100, 
            is_optional_field=False
        )
        verify_name_complexity(value, False)

        return value
    
    def validate_mensaje(self, value):
        verify_value_length(
            value=value, 
            min_size=0, 
            max_size=5000, 
            is_optional_field=False
        )

        return value


class UserSerializer(serializers.ModelSerializer):
    recaptcha = ReCaptchaV2Field()

    class Meta:
        model = User
        fields = '__all__'
        extra_kwargs = {
            'password': {'write_only': True},
        }

    # ----- get_fields ----- OK
    def get_fields(self):
        fields = super().get_fields()
        fields.update({'recaptcha': ReCaptchaV2Field()})
        return fields
    
    # ----- validate ----- OK
    def validate(self, attrs):
        attrs.pop("recaptcha")
        return attrs
    
    # ----- validate_name ----- OK
    def validate_name(self, value):
        verify_value_length(
            value=value, 
            min_size=2, 
            max_size=100, 
            is_optional_field=True
        )
        verify_name_complexity(value, True)

        return value

    # ----- validate_email ----- OK
    def validate_email(self, value):
        verify_value_length(
            value=value, 
            min_size=6, 
            max_size=250, 
            is_optional_field=False
        )
        verify_email_complexity(value)
        verify_email_is_blacklisted(value)

        return value
    
    # ----- validate_password ----- OK
    def validate_password(self, value):
        verify_value_length(
            value=value, 
            min_size=8, 
            max_size=128, 
            is_optional_field=False
        )
        verify_password_complexity(value)
        use_default_password_validators(value)

        return value

    def to_representation(self, instance):
        data = {
            'id': instance.id,
            'name': instance.name,
            'email': instance.email,
            'is_active': instance.is_active,
            'is_staff': instance.is_staff,
        }
        return data

    # ----- CREATE ----- OK
    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        user.save()
        return user

    # ----- UPDATE ----- OK
    def update(self, instance, validated_data):
        user = super().update(instance, validated_data)
        user.set_password(validated_data['password'])
        user.save()
        return user


# OK
class PictogramaSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Pictograma
        fields = '__all__'

    # ----- validate_autor ----- OK
    def validate_autor(self, value):
        if not value:
            msg = 'Se requiere este campo en los datos.'
            raise serializers.ValidationError(msg)
        
        if not value.is_active:
            raise serializers.ValidationError('Usuario inactivo.')
        
        if self.instance:
            if value == self.instance.autor:
                return value

        return value

    # ----- validate_nombre ----- OK
    def validate_nombre(self, value):
        if self.instance:
            if value == self.instance.nombre:
                return value
        
        verify_content_name(value)

        return value
    
    # ----- validate_ruta ----- OK
    def validate_ruta(self, value):
        model = self.Meta.model
        model_name = model._meta.verbose_name

        if self.instance:
            if value == self.instance.ruta:
                return value
            
        user = get_user_instance(
            self.initial_data.get('autor', None), 
            User
        )
        
        verify_file_type(value, model_name)
        verify_file_size(value, user)
        
        return value

    # ----- CREATE ----- OK
    def create(self, validated_data):
        object = create_content(
            content_model=self.Meta.model,
            user_model=User,
            content_folder='pictograms',
            validated_data=validated_data
        )
        object.save()

        return object
    
    # ----- UPDATE ----- OK
    def update(self, instance, validated_data):
        model_instance = update_content(
            user_model=User, 
            content_folder='pictograms', 
            instance=instance, 
            validated_data=validated_data
        )
        model_instance.save()

        return model_instance


class AudioSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Audio
        fields = '__all__'

    # ----- validate_autor ----- OK
    def validate_autor(self, value):
        if not value:
            msg = 'Se requiere este campo en los datos.'
            raise serializers.ValidationError(msg)
        
        if not value.is_active:
            raise serializers.ValidationError('Usuario inactivo.')
        
        if self.instance:
            if value == self.instance.autor:
                return value

        return value

    # ----- validate_nombre ----- OK
    def validate_nombre(self, value):
        if self.instance:
            if value == self.instance.nombre:
                return value
        
        verify_content_name(value)

        return value
    
    # ----- validate_ruta ----- OK
    def validate_ruta(self, value):
        model = self.Meta.model
        model_name = model._meta.verbose_name

        if self.instance:
            if value == self.instance.ruta:
                return value
        
        user = get_user_instance(
            self.initial_data.get('autor', None), 
            User
        )
        
        verify_file_type(value, model_name)
        verify_file_size(value, user)
        
        return value

    # ----- CREATE -----
    def create(self, validated_data):
        object = create_content(
            content_model=self.Meta.model,
            user_model=User,
            content_folder='sounds',
            validated_data=validated_data
        )
        object.save()

        return object
    
    # ----- UPDATE -----
    def update(self, instance, validated_data):
        model_instance = update_content(
            user_model=User, 
            content_folder='sounds', 
            instance=instance, 
            validated_data=validated_data
        )
        model_instance.save()

        return model_instance
    

class RutinaSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Rutina
        fields = '__all__'

    # ----- validate_autor ----- OK
    def validate_autor(self, value):
        if not value:
            msg = 'Se requiere este campo en los datos.'
            raise serializers.ValidationError(msg)
        
        if not value.is_active:
            raise serializers.ValidationError('Usuario inactivo.')
        
        if self.instance:
            if value == self.instance.autor:
                return value

        return value

    # ----- validate_nombre -----
    def validate_nombre(self, value):
        verify_content_name(value)

        return value
    
    # ----- validate_url_portada -----
    def validate_url_portada(self, value):
        model = self.Meta.model
        model_name = model._meta.verbose_name

        if value:
            if self.instance:
                if value == self.instance.url_portada:
                    return value
        
            user = get_user_instance(
                self.initial_data.get('autor', None), 
                User
            )
            
            verify_file_type(value, model_name)
            verify_file_size(value, user)
        
        return value
    
    # ----- CREATE -----
    def create(self, validated_data):
        object = create_routine(
            content_model=self.Meta.model,
            user_model=User,
            content_folder='covers',
            validated_data=validated_data
        )
        object.save()

        return object
    
    # ----- UPDATE -----
    def update(self, instance, validated_data):
        model_instance = update_routine_instance(
            content_model=self.Meta.model,
            user_model=User, 
            content_folder='covers', 
            instance=instance, 
            validated_data=validated_data
        )
        model_instance.save()

        return model_instance
