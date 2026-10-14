from pathlib import Path
from uuid import uuid4


def game_artwork_path(instance, filename):
    extension = Path(filename).suffix.lower()
    return f'game_icons/{uuid4().hex}{extension}'
