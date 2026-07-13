from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("portal", "0005_sitesetting_external_links"),
    ]

    operations = [
        migrations.AddField(
            model_name="sitesetting",
            name="banner_interval_seconds",
            field=models.PositiveSmallIntegerField(default=6, verbose_name="横幅切换间隔（秒）"),
        ),
    ]
