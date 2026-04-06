from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from books.models import Post


class Command(BaseCommand):
    def handle(self, *args, **options):
        content_type = ContentType.objects.get_for_model(Post)

        add_post = Permission.objects.get(codename='add_post', content_type=content_type)
        change_post = Permission.objects.get(codename='change_post', content_type=content_type)
        delete_post = Permission.objects.get(codename='delete_post', content_type=content_type)
        view_post = Permission.objects.get(codename='view_post', content_type=content_type)

        admin_group, _ = Group.objects.get_or_create(name='Admin')
        admin_group.permissions.set([add_post, change_post, delete_post, view_post])

        user_group, _ = Group.objects.get_or_create(name='User')
        user_group.permissions.set([view_post])

        self.stdout.write("Groups created: Admin (full CRUD), User (READ only)")
