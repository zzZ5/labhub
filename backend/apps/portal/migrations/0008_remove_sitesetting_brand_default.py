from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("portal", "0007_clean_portal_field_semantics"),
    ]

    operations = [
        migrations.AlterField(
            model_name="sitesetting",
            name="site_name",
            field=models.CharField(blank=True, default="", max_length=120, verbose_name="站点名称"),
        ),
    ]
