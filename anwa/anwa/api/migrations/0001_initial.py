# Generated by Django 4.2.19 on 2025-02-18 01:57

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Categorias',
            fields=[
                ('idCategoria', models.AutoField(primary_key=True, serialize=False)),
                ('descripcionCat', models.CharField(max_length=255)),
                ('obsCat', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Documento',
            fields=[
                ('id_documento', models.AutoField(primary_key=True, serialize=False)),
                ('id_transaccion', models.IntegerField()),
                ('descripcion', models.TextField()),
                ('afectacion', models.TextField()),
                ('consecutivo', models.CharField(max_length=255)),
                ('obsDocumento', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Inventario',
            fields=[
                ('id_producto', models.AutoField(primary_key=True, serialize=False)),
                ('stock_min', models.IntegerField()),
                ('stock_max', models.IntegerField()),
                ('descripcion', models.TextField()),
                ('saldo_ini', models.IntegerField()),
                ('saldo', models.IntegerField()),
                ('nivel_alerta', models.IntegerField()),
                ('entradas', models.IntegerField()),
                ('salidas', models.IntegerField()),
                ('obsProd', models.TextField()),
                ('categoria', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='productos', to='api.categorias')),
            ],
        ),
        migrations.CreateModel(
            name='ModeloPrueba',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Movimiento',
            fields=[
                ('id_movimiento', models.AutoField(primary_key=True, serialize=False)),
                ('nombre', models.CharField(max_length=255)),
                ('precio', models.FloatField()),
                ('descripcion', models.TextField()),
                ('obs_movimiento', models.TextField()),
                ('id_producto', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='movimientos', to='api.inventario')),
            ],
        ),
        migrations.CreateModel(
            name='Roles',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('nombre', models.CharField(max_length=255, unique=True)),
                ('descripcion', models.TextField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Usuario',
            fields=[
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('correo', models.EmailField(max_length=254, unique=True)),
                ('nombre', models.CharField(max_length=255)),
                ('telefono', models.CharField(blank=True, max_length=20, null=True)),
                ('direccion', models.TextField(blank=True, null=True)),
                ('is_active', models.BooleanField(default=True)),
                ('is_staff', models.BooleanField(default=False)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to.', related_name='usuario_set', to='auth.group')),
                ('roles', models.ManyToManyField(blank=True, related_name='usuarios', to='api.roles')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='usuario_set', to='auth.permission')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Transaccion',
            fields=[
                ('id_transaccion', models.AutoField(primary_key=True, serialize=False)),
                ('obs_Transaccion', models.TextField()),
                ('id_documento', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='transacciones', to='api.documento')),
                ('id_movimiento', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='transacciones', to='api.movimiento')),
                ('id_usuario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='transacciones', to='api.usuario')),
            ],
        ),
        migrations.AddField(
            model_name='documento',
            name='id_usuario_genera',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='documentos_generados', to='api.usuario'),
        ),
    ]
