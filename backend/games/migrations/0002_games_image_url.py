from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [('games', '0001_initial')]
    operations = [migrations.AddField(model_name='games', name='image_url', field=models.URLField(blank=True, default='', max_length=2048))]
