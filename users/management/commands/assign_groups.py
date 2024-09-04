from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from users.models import User
from courses.models import Course

class Command(BaseCommand):
    help = 'Create user groups and assign them to users'

    def handle(self, *args, **kwargs):
        # Create groups if they don't exist
        teachers_group, created = Group.objects.get_or_create(name='Teachers')
        students_group, created = Group.objects.get_or_create(name='Students')

        print(f'Group "Teachers" {"created" if created else "already exists"}.')
        print(f'Group "Students" {"created" if created else "already exists"}.')

        # Assign permissions to the groups
        content_type = ContentType.objects.get_for_model(Course)
        manage_courses_permission = Permission.objects.get(codename='can_manage_courses', content_type=content_type)
        teachers_group.permissions.add(manage_courses_permission)
        print('Permission "can_manage_courses" added to "Teachers" group.')

        # Assign users to groups based on their user_type
        for user in User.objects.all():
            if user.is_superuser:
                continue  # Skip the superuser

            if user.user_type == 'teacher':
                group_name = 'Teachers' 
            elif user.user_type == 'student':
                group_name = 'Students'
            group = Group.objects.get(name=group_name)
            user.groups.add(group)
            self.stdout.write(self.style.SUCCESS(f'User "{user.username}" added to "{group_name}" group.'))
        
        self.stdout.write(self.style.SUCCESS('All users assigned to their respective groups.'))