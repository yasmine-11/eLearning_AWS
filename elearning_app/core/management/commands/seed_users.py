import csv
from django.core.management.base import BaseCommand
from users.models import User, StatusUpdate
from django.conf import settings
from django.contrib.auth.hashers import make_password
import os

class Command(BaseCommand):
    help = 'Seed users and status updates from CSV files'

    def handle(self, *args, **kwargs):
        csv_files_dir = os.path.join(settings.BASE_DIR, 'csv_files')

        # Load users
        users_csv_path = os.path.join(csv_files_dir, 'users.csv')
        with open(users_csv_path, 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                password = make_password(row['password'])
                User.objects.create(
                    username=row['username'],
                    password=password, 
                    real_name=row['real_name'],
                    photo=row['photo'],
                    user_type=row['user_type']
                )

        # Load status updates
        status_csv_path = os.path.join(csv_files_dir, 'status.csv')
        with open(status_csv_path, 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                StatusUpdate.objects.create(
                    user_id=row['user_id'],
                    content=row['content']
                )

        self.stdout.write(self.style.SUCCESS('Successfully seeded users and status updates'))
