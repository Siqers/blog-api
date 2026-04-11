from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()

class Command(BaseCommand):
    help = 'Seed the database with test data'

    def handle(self, *args, **kwargs):
        self.stdout.write('Seeding database...')

        # Create users
        if not User.objects.filter(email='admin@example.com').exists():
            User.objects.create_superuser(
                email='admin@example.com',
                password='admin123',
            )
            self.stdout.write('Created admin user')

        if not User.objects.filter(email='user@example.com').exists():
            User.objects.create_user(
                email='user@example.com',
                password='user123',
            )
            self.stdout.write('Created test user')

        # Create posts
        from apps.blog.models import Post, Category
        user = User.objects.get(email='admin@example.com')

        if not Category.objects.filter(slug='general').exists():
            category = Category.objects.create(slug='general')
            self.stdout.write('Created category')
        else:
            category = Category.objects.get(slug='general')

        if not Post.objects.filter(slug='hello-world').exists():
            Post.objects.create(
                title='Hello World',
                slug='hello-world',
                body='This is a test post.',
                author=user,
                category=category,
                status='published',
            )
            self.stdout.write('Created test post')

        self.stdout.write(self.style.SUCCESS('Database seeded successfully!'))