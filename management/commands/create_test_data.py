from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils.text import slugify
from django.utils.timezone import now
from faker import Faker
import random
import uuid

from octopusdash.models import (
    Book,
    NumberFields,
    TimeFields,
    FileFields,
    RelationFields,
    OtherFields,
)

User = get_user_model()
fake = Faker()


class Command(BaseCommand):
    help = "Create fake test data for all models"

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING("Creating test data..."))

        # --- Users ---
        users = []
        for _ in range(30):
            user = User.objects.create_user(
                username=fake.user_name(),
                email=fake.email(),
                password="password123"
            )
            users.append(user)
        self.stdout.write(self.style.SUCCESS("✅ 10 Users created"))

        # --- Books ---
        books = []
        for _ in range(30):
            book = Book.objects.create(
                author=random.choice(users),
                field_with_choices=random.choice([c[0] for c in Book.C.choices]),
                name=fake.sentence(nb_words=3),
                text=fake.paragraph(),
                first_published=fake.date_this_century(),
                is_free=random.choice([True, False]),
            )
            books.append(book)
        self.stdout.write(self.style.SUCCESS("✅ 10 Books created"))

        # --- NumberFields ---
        for _ in range(30):
            NumberFields.objects.create(
                positive_integer=fake.random_int(min=1, max=1000),
                integer=fake.random_int(min=-500, max=500),
                big_integer=fake.random_int(min=10**5, max=10**9),
                small_integer=fake.random_int(min=-100, max=100),
                float_number=random.uniform(1, 500),
                decimal_number=fake.pydecimal(left_digits=6, right_digits=2, positive=True),
            )
        self.stdout.write(self.style.SUCCESS("✅ 10 NumberFields created"))

        # --- TimeFields ---
        for _ in range(30):
            TimeFields.objects.create(
                birthday=fake.date_of_birth(minimum_age=18, maximum_age=80),
                wake_up_time=fake.time_object(),
                duration=fake.time_delta(),
            )
        self.stdout.write(self.style.SUCCESS("✅ 10 TimeFields created"))

        # --- FileFields (fake names only) ---
        for _ in range(30):
            FileFields.objects.create(
                file="files/fake_file.txt",
                image="images/fake_image.jpg",
            )
        self.stdout.write(self.style.SUCCESS("✅ 10 FileFields created"))

        # --- RelationFields ---
        for i in range(30):
            rel = RelationFields.objects.create(
                one_to_one=users[i % len(users)],
            )
            rel.many_to_many.set(random.sample(books, k=min(3, len(books))))
        self.stdout.write(self.style.SUCCESS("✅ 10 RelationFields created"))

        # --- OtherFields ---
        for _ in range(30):
            OtherFields.objects.create(
                slug=slugify(fake.unique.word()),
                email=fake.email(),
                url=fake.url(),
                uuid=uuid.uuid4(),
                ip_address=fake.ipv4(),
                json_data={"key": fake.word(), "value": fake.random_int()},
            )
        self.stdout.write(self.style.SUCCESS("✅ 10 OtherFields created"))

        self.stdout.write(self.style.SUCCESS("🎉 All test data created successfully!"))
