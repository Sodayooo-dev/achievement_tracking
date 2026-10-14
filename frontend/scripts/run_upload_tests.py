import os
import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd()))
os.environ['DJANGO_SETTINGS_MODULE'] = 'upload_test_settings'
import django
django.setup()
from django.test.runner import DiscoverRunner
sys.exit(bool(DiscoverRunner(verbosity=2).run_tests(['games.test_uploads', 'config.test_workflows'])))
