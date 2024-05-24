from django.db import models
from django.conf import settings
from datetime import datetime
from django.contrib.auth.models import AbstractUser, Permission
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
import os
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

def get_image_upload_path(instance, filename):
    base_path = 'news'
    news_id = instance.noticia.id_noticia
    existing_images = instance.noticia.imagenes.count()
    new_filename = f"{news_id}-{existing_images + 1}{os.path.splitext(filename)[1]}"
    return os.path.join(base_path, str(news_id), new_filename)

class Noticia(models.Model):
    id_noticia = models.AutoField(db_column='id_noticia', primary_key=True)
    titulo_noticia = models.CharField(max_length=100, blank=False, null=False)
    cuerpo_noticia = models.TextField(blank=False, null=False, default='')
    id_categoria = models.ForeignKey('Categoria', on_delete=models.PROTECT, db_column='id_categoria')
    id_pais = models.ForeignKey('Pais', on_delete=models.PROTECT, db_column='id_pais', null=True)
    activo = models.BooleanField(("Activo"), default=True)
    destacada = models.BooleanField(("Destacada"), default=False)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)
    id_usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, db_column='id_usuario')
    eliminado = models.BooleanField(("Borrado"), default=False)
    
    def __str__(self):
        return self.titulo_noticia

class DetalleNoticia(models.Model):
    id_detalle = models.AutoField(db_column='id_detalle', primary_key=True)
    noticia = models.OneToOneField(Noticia, on_delete=models.CASCADE, related_name='detalle')
    comentario = models.TextField(blank=True, null=True)
    ESTADO_CHOICES = (
        ('A', 'Aprobado'),
        ('R', 'Rechazado'),
    )
    estado = models.CharField(max_length=1, choices=ESTADO_CHOICES, blank=True, null=True)
    id_usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, blank=True, null=True)
    publicacion = models.DateTimeField(blank=True, null=True, default=None)
    publicada = models.BooleanField(default=False)

    def __str__(self):
        return f'Detalle {self.id_detalle} - Noticia: {self.noticia.titulo_noticia}'

    
@receiver(post_save, sender=Noticia)
def create_detalle_noticia(sender, instance, created, **kwargs):
    if created:
        DetalleNoticia.objects.create(noticia=instance)

class ImagenNoticia(models.Model):
    id_imagen = models.AutoField(db_column='id_imagen', primary_key=True)
    noticia = models.ForeignKey(Noticia, on_delete=models.CASCADE, related_name='imagenes')
    imagen = models.ImageField(upload_to=get_image_upload_path, null=True, blank=True)

    def __str__(self):
        return f'Imagen {self.id_imagen} - Noticia: {self.noticia.titulo_noticia}'

class Pais(models.Model):
    id_pais = models.AutoField(db_column='id_pais', primary_key=True)
    pais = models.CharField(max_length=20, blank=True, null=False)
    
    def __str__(self):
        return self.pais

class Categoria(models.Model):
    id_categoria = models.AutoField(db_column='id_categoria', primary_key=True)
    nombre_categoria = models.CharField(max_length=20, blank=False, null=False)

    def __str__(self):
        return str(self.nombre_categoria)


class Usuario(AbstractUser):
    ROLES = (
        ('administrador', 'Administrador'),
        ('editor', 'Editor'),
        ('periodista', 'Periodista'),
        ('lector', 'Lector'),
    )

    role = models.CharField(max_length=15, choices=ROLES, default='lector')

    def __str__(self):
        return self.username

    class Meta:
        swappable = 'AUTH_USER_MODEL'
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'