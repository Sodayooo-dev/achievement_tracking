from django.db import migrations, models
import games.artwork


class Migration(migrations.Migration):
    dependencies = [('games', '0002_games_image_url')]
    operations = [migrations.AddField(model_name='games', name='image', field=models.ImageField(blank=True, default='', upload_to=games.artwork.game_artwork_path))]
