from django.core.management.base import BaseCommand
from account.models import LanguagePreferenceModel

class Command(BaseCommand):
    help = 'Populates the LanguagePreference model with default values.'

    def handle(self, *args, **kwargs):
        languages = [
            {'code': 'en-US', 'name': 'English'},
            {'code': 'hi-IN', 'name': 'Hindi'},
            {'code': 'gu-IN', 'name': 'Gujarati'},
            {'code': 'kn-IN', 'name': 'Kannada'},
            {'code': 'ml-IN', 'name': 'Malayalam'},
            {'code': 'mr-IN', 'name': 'Marathi'},
            {'code': 'ta-IN', 'name': 'Tamil'},
            {'code': 'te-IN', 'name': 'Telugu'},
            {'code': 'bn-IN', 'name': 'Bengali'},
        ]

        for lang in languages:
            obj, created = LanguagePreferenceModel.objects.get_or_create(
                code=lang['code'],
                defaults={'name': lang['name']}
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"Added {lang['name']}"))
            else:
                self.stdout.write(self.style.WARNING(f"{lang['name']} already exists."))

        self.stdout.write(self.style.SUCCESS("Language preferences populated successfully."))
