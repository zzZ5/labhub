from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("portal", "0003_sitesetting_hero_image"),
    ]

    operations = [
        migrations.AddField(
            model_name="researchdirection",
            name="keywords",
            field=models.CharField(blank=True, max_length=240, verbose_name="关键词"),
        ),
    ]
