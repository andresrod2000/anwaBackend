# Generated by Django 4.2.19 on 2025-06-19 01:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0003_roles_grupo'),
    ]

    operations = [
        migrations.CreateModel(
            name='Conversacion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('numero_telefono', models.CharField(db_index=True, max_length=20)),
                ('mensaje', models.TextField()),
                ('es_usuario', models.BooleanField(default=True)),
                ('fecha_hora', models.DateTimeField(auto_now_add=True, db_index=True)),
            ],
            options={
                'ordering': ['fecha_hora'],
                'indexes': [models.Index(fields=['numero_telefono', 'fecha_hora'], name='api_convers_numero__c09e59_idx')],
            },
        ),
    ]
