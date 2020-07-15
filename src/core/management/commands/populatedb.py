from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.db import connection

from src.utils.import_data import create_towns

class Command(BaseCommand):
    help = "Populate database with test objects"


    def make_database_faster(self):
        """Sacrifice some of the safeguards of sqlite3 for speed."""
        
        if "sqlite3" in connection.settings_dict["ENGINE"]:
            cursor = connection.cursor()
            cursor.execute("PRAGMA temp_store = MEMORY;")
            cursor.execute("PRAGMA synchronous = OFF;")


    def handle(self, *args, **options):
        self.make_database_faster()
        
        create_towns()
        self.stdout.write("Created town")