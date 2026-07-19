import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("publications", "0004_clear_missing_impact_factors")]

    operations = [
        migrations.AddField(model_name="publication", name="view_count", field=models.PositiveIntegerField(default=0, verbose_name="浏览次数")),
        migrations.AddField(model_name="project", name="view_count", field=models.PositiveIntegerField(default=0, verbose_name="浏览次数")),
        migrations.AddField(model_name="project", name="created_at", field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now, verbose_name="创建时间"), preserve_default=False),
        migrations.AddField(model_name="project", name="updated_at", field=models.DateTimeField(auto_now=True, default=django.utils.timezone.now, verbose_name="更新时间"), preserve_default=False),
        migrations.AddField(model_name="patent", name="view_count", field=models.PositiveIntegerField(default=0, verbose_name="浏览次数")),
        migrations.AddField(model_name="patent", name="created_at", field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now, verbose_name="创建时间"), preserve_default=False),
        migrations.AddField(model_name="patent", name="updated_at", field=models.DateTimeField(auto_now=True, default=django.utils.timezone.now, verbose_name="更新时间"), preserve_default=False),
        migrations.AddField(model_name="award", name="view_count", field=models.PositiveIntegerField(default=0, verbose_name="浏览次数")),
        migrations.AddField(model_name="award", name="created_at", field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now, verbose_name="创建时间"), preserve_default=False),
        migrations.AddField(model_name="award", name="updated_at", field=models.DateTimeField(auto_now=True, default=django.utils.timezone.now, verbose_name="更新时间"), preserve_default=False),
    ]
