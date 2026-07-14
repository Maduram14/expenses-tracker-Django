from django.core.management.base import BaseCommand
from tracker.models import Category

DEFAULTS = [
    ('Food', '#f97316'),
    ('Transport', '#3b82f6'),
    ('Shopping', '#ec4899'),
    ('Bills & Utilities', '#ef4444'),
    ('Entertainment', '#8b5cf6'),
    ('Health', '#10b981'),
    ('Rent', '#0ea5e9'),
    ('Other', '#6b7280'),
]


class Command(BaseCommand):
    help = 'Seed default expense categories'

    def handle(self, *args, **options):
        created = 0
        for name, color in DEFAULTS:
            _, was_created = Category.objects.get_or_create(name=name, defaults={'color': color})
            if was_created:
                created += 1
        self.stdout.write(self.style.SUCCESS(f'Done. {created} new categories created.'))
