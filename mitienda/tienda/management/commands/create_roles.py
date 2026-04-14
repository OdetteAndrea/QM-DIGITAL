from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User
from tienda.models import Producto


class Command(BaseCommand):
    help = 'Crea roles para la tienda  y asigna permisos'

    def handle(self, *args, **options):
        roles = {
            'Administrador': [
                'add_user',
                'change_user',
                'delete_user',
                'view_user',
                'add_producto',
                'change_producto',
                'delete_producto',
                'view_producto',
            ],
            'Supervisor': [
                'view_user',
                'change_user',
                'view_producto',
                'change_producto',
            ],
            'Cliente': [
                'view_user',
            ],
        }

        content_type = ContentType.objects.get_for_model(User)
        producto_ct = ContentType.objects.get_for_model(Producto)

        for role, perms in roles.items():
            group, created = Group.objects.get_or_create(name=role)
            for perm in perms:
                # Determinar a qué ContentType pertenece el permiso
                if 'user' in perm:
                    ct = content_type
                elif 'producto' in perm:
                    ct = producto_ct
                else:
                    continue
                    
                permission = Permission.objects.get(
                    codename=perm,
                    content_type=ct
                )
                group.permissions.add(permission)

            self.stdout.write(self.style.SUCCESS(
                f'Roles creados/actualizados: {role}'))

        # --- CREACIÓN AUTOMÁTICA DE USUARIOS DE PRUEBA ---
        
        # 1. Crear usuario Administrador
        if not User.objects.filter(username='admin').exists():
            admin_user = User.objects.create_superuser('admin', 'admin@odette.cl', 'admin1234')
            admin_group = Group.objects.get(name='Administrador')
            admin_user.groups.add(admin_group)
            self.stdout.write(self.style.SUCCESS('Usuario administrador creado con éxito (admin / admin1234)'))
        else:
            self.stdout.write(self.style.WARNING('El usuario "admin" ya existe. Omitiendo creación.'))

        # 2. Crear usuario Cliente
        if not User.objects.filter(username='cliente').exists():
            cliente_user = User.objects.create_user('cliente', 'cliente@odette.cl', 'cliente1234')
            cliente_group = Group.objects.get(name='Cliente')
            cliente_user.groups.add(cliente_group)
            self.stdout.write(self.style.SUCCESS('Usuario cliente creado con éxito (cliente / cliente1234)'))
        else:
            self.stdout.write(self.style.WARNING('El usuario "cliente" ya existe. Omitiendo creación.'))
