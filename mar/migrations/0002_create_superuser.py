# Create initial superuser
import logging
from decouple import config
from django.db import migrations
import secrets
import string

logger = logging.getLogger('console')

def generate_superuser(apps, schema_editor):
    from django.contrib.auth import get_user_model

    USERNAME = config("ADMIN_USERNAME", "admin")
    PASSWORD = config("ADMIN_PASSWORD", ''.join(secrets.choice(string.ascii_letters + string.digits + string.punctuation) for i in range(20)))
    EMAIL = config("ADMIN_EMAIL", "admin@domain.local")

    user = get_user_model()

    if not user.objects.filter(username=USERNAME, email=EMAIL).exists():
        logger.info(f'Creating new superuser: {USERNAME}')
        admin = user.objects.create_superuser(
           username=USERNAME, password=PASSWORD, email=EMAIL
        )
        # Tell user default password if didn't pull from environment vars
        if not config("ADMIN_USERNAME", False):
            logger.info(f'\n\tSuperuser password not in environment vars, set to: "{default_pass}"')
        else:
            logger.info(f'\tSuperuser password set from ADMIN_PASSWORD environment variable')
            
        admin.save()
    else:
        logger.info("\n\tSuperuser already created!")


class Migration(migrations.Migration):
    dependencies = [
        # Dependencies to other migrations
        ('mar', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(generate_superuser),
    ]