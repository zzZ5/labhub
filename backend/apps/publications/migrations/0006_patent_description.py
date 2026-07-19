from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("publications", "0005_public_detail_stats")]

    operations = [
        migrations.AddField(
            model_name="patent",
            name="description",
            field=models.TextField(blank=True, verbose_name="说明"),
        ),
    ]
