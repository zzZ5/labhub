from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("portal", "0006_sitesetting_banner_interval_seconds"),
    ]

    operations = [
        migrations.RenameField(
            model_name="sitesetting",
            old_name="keywords",
            new_name="hero_subtitle",
        ),
        migrations.AlterField(
            model_name="sitesetting",
            name="hero_subtitle",
            field=models.CharField(blank=True, max_length=300, verbose_name="首页横幅副标题"),
        ),
        migrations.RemoveField(
            model_name="researchdirection",
            name="keywords",
        ),
    ]
