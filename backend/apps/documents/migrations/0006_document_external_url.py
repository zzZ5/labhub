from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("documents", "0005_remove_documentpermission_created_by_and_more")]

    operations = [
        migrations.AddField(
            model_name="document",
            name="external_url",
            field=models.URLField(blank=True, max_length=500, verbose_name="外部视频链接"),
        ),
    ]
