# Generated by Django 4.2.3 on 2023-07-12 05:31

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('CaosNewsApp', '0020_rename_id_detallenoticia_id_detalle'),
    ]

    operations = [
        migrations.RenameField(
            model_name='detallenoticia',
            old_name='revisada_y_publicada',
            new_name='publicada',
        ),
    ]
