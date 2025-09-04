from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from faker import Faker
import random

User = get_user_model()
fake = Faker()

class Command(BaseCommand):
    help = "Create fake users for testing"

    def add_arguments(self, parser):
        parser.add_argument(
            "--total",
            type=int,
            default=10,
            help="Number of fake users to create (default: 10)",
        )

    def handle(self, *args, **kwargs):
        total = kwargs["total"]

        for _ in range(total):
            username = fake.user_name()
            email = fake.email()
            password = "password123"  # default password for all
            first_name = fake.first_name()
            last_name = fake.last_name()

            if not User.objects.filter(username=username).exists():
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password,
                    first_name=first_name,
                    last_name=last_name,
                )
                self.stdout.write(self.style.SUCCESS(f"✅ Created user: {user.username}"))
            else:
                self.stdout.write(self.style.WARNING(f"⚠️ Skipped duplicate username: {username}"))
