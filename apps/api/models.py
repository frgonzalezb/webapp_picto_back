from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models

from simple_history.models import HistoricalRecords

from .managers import UserManager


class User(AbstractBaseUser, PermissionsMixin):
    name = models.CharField(max_length=255, blank=True, default='')
    email = models.EmailField(max_length=254, unique=True)
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    inactive_since = models.DateTimeField(null=True, blank=True)

    storage_limit = models.PositiveIntegerField(default=20 * 1024 * 1024)  # 20 MB in bytes
    
    objects = UserManager()
    log = HistoricalRecords(related_name='history')
    

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    USERNAME_FIELD = 'email'
    
    def __str__(self):
        return f'{self.email}'
    

class AccountActivationToken(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=128, unique=True)


class Pictograma(models.Model):
    nombre = models.CharField('Nombre', max_length=50)
    ruta = models.ImageField(
        'Ruta', 
        upload_to='',
        max_length=255
    )
    fecha_subida = models.DateTimeField(auto_now_add=True)
    ultima_modificacion = models.DateTimeField(auto_now=True)
    es_precargado = models.BooleanField(default=False)

    autor = models.ForeignKey(User, on_delete=models.CASCADE)
    log = HistoricalRecords(related_name='history')
    
    class Meta:
        verbose_name = 'Pictograma'
        verbose_name_plural = 'Pictogramas'

    def __str__(self):
        return f'Pictograma "{self.nombre}" subido por {self.autor.email}'


class Audio(models.Model):
    nombre = models.CharField('Nombre', max_length=50)
    ruta = models.FileField(
        'Ruta', 
        upload_to='', 
        max_length=255
    )
    fecha_subida = models.DateTimeField(auto_now_add=True)
    ultima_modificacion = models.DateTimeField(auto_now=True)
    es_precargado = models.BooleanField(default=False)

    autor = models.ForeignKey(User, on_delete=models.CASCADE)
    log = HistoricalRecords(related_name='history')
    
    class Meta:
        verbose_name = 'Audio'
        verbose_name_plural = 'Audios'

    def __str__(self):
        return f'Audio "{self.nombre}" subido por {self.autor.email}'
    

class Rutina(models.Model):
    nombre = models.CharField('Nombre', max_length=50)
    json_rutina = models.TextField('JSON de la rutina', default="")
    url_portada = models.ImageField(
        'URL de la portada', 
        upload_to='',
        max_length=255,
        null=True,
        blank=True,
        default=""
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    ultima_modificacion = models.DateTimeField(auto_now=True)

    autor = models.ForeignKey(User, on_delete=models.CASCADE)
    log = HistoricalRecords(related_name='history')

    class Meta:
        verbose_name = 'Rutina'
        verbose_name_plural = 'Rutinas'

    def __str__(self):
        return f'Rutina "{self.nombre}" creada por {self.autor.email}'
