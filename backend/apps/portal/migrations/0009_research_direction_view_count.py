from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("portal", "0008_remove_sitesetting_brand_default")]

    operations = [
        migrations.AddField(
            model_name="researchdirection",
            name="view_count",
            field=models.PositiveIntegerField(default=0, verbose_name="浏览次数"),
        ),
    ]
