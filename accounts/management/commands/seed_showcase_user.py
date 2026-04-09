from django.core.management.base import BaseCommand

from accounts.showcase import (
    SHOWCASE_PASSWORD,
    SHOWCASE_USERNAME,
    seed_showcase_user,
)


class Command(BaseCommand):
    help = "Create or refresh the Sarvesh Kumar showcase user and demo dashboard data."

    def handle(self, *args, **options):
        result = seed_showcase_user()
        self.stdout.write(
            self.style.SUCCESS(
                "Seeded showcase user "
                f"'{SHOWCASE_USERNAME}' with {result['course_count']} courses and {result['task_count']} tasks. "
                f"Password: {SHOWCASE_PASSWORD}"
            )
        )
