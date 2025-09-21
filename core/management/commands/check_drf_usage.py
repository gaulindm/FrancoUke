import os
import sys
import fnmatch
import importlib
from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Check if Django REST Framework is being used in the project."

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("🔍 Checking for Django REST Framework usage...\n"))

        drf_installed = "rest_framework" in settings.INSTALLED_APPS
        if drf_installed:
            self.stdout.write(self.style.SUCCESS("✔️ 'rest_framework' found in INSTALLED_APPS"))
        else:
            self.stdout.write(self.style.WARNING("❌ 'rest_framework' not found in INSTALLED_APPS"))

        # Scan project files for DRF imports
        drf_imports = []
        for root, _, files in os.walk(settings.BASE_DIR):
            for filename in fnmatch.filter(files, "*.py"):
                file_path = os.path.join(root, filename)
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()
                        if "rest_framework" in content:
                            drf_imports.append(file_path)
                except Exception as e:
                    self.stderr.write(f"⚠️ Could not read {file_path}: {e}")

        if drf_imports:
            self.stdout.write(self.style.SUCCESS("✔️ Found DRF imports in:"))
            for file in drf_imports:
                self.stdout.write(f"   - {file}")
        else:
            self.stdout.write(self.style.WARNING("❌ No DRF imports found in project code."))

        # Check for routers / api_view in urls.py files
        urls_with_drf = []
        for root, _, files in os.walk(settings.BASE_DIR):
            for filename in fnmatch.filter(files, "urls.py"):
                file_path = os.path.join(root, filename)
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()
                        if any(keyword in content for keyword in ["DefaultRouter", "SimpleRouter", "api_view"]):
                            urls_with_drf.append(file_path)
                except Exception as e:
                    self.stderr.write(f"⚠️ Could not read {file_path}: {e}")

        if urls_with_drf:
            self.stdout.write(self.style.SUCCESS("✔️ Found DRF routing in:"))
            for file in urls_with_drf:
                self.stdout.write(f"   - {file}")
        else:
            self.stdout.write(self.style.WARNING("❌ No DRF routers/api_view found in urls.py files."))

        # Final verdict
        if drf_installed or drf_imports or urls_with_drf:
            self.stdout.write(self.style.SUCCESS("\n✅ DRF appears to be in use somewhere in your project."))
        else:
            self.stdout.write(self.style.ERROR("\n🚫 DRF does not appear to be used in this project."))
