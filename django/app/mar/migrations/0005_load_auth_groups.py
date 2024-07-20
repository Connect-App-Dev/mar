from django.db import migrations
#from django.core.serializers import base, python
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from mar.models import Mac


def apply_migration(apps, schema_editor):
    macContentType = ContentType.objects.get_for_model(Mac)

    #Create MAR Manager Role and Assign Permissions
    mar_manager, created = Group.objects.get_or_create(name='MAR Manager (Use "MAC Address Groups: User & Permissions Assignment" for RLS)')
    add_mac = Permission.objects.create(codename='add_mac', name='Can add MAC', content_type=macContentType)
    update_mac = Permission.objects.create(codename='change_mac', name='Can change MAC', content_type=macContentType)
    del_mac = Permission.objects.create(codename='delete_mac', name='Can delete MAC', content_type=macContentType)
    view_mac = Permission.objects.create(codename='view_mac', name='Can view MAC', content_type=macContentType)
    mar_manager.permissions.add(add_mac, update_mac, del_mac, view_mac)


def revert_migration(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    Group.objects.filter(name='MAR Manager (Use "MAC Address Groups: User & Permissions Assignment" for RLS)').delete()

class Migration(migrations.Migration):
    dependencies = [
        # Dependencies to other migrations
        ('contenttypes', '0001_initial'),
        ('sessions', '0001_initial'),
        ('mar', '0004_load_groups'),
    ]

    operations = [
        migrations.RunPython(apply_migration, revert_migration)
    ]