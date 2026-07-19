from django.db import migrations, models
from django.db.models import F


def populate_published_at(apps, schema_editor):
    NewsArticle = apps.get_model("news", "NewsArticle")
    NewsArticle.objects.filter(status="published", published_at__isnull=True).update(published_at=F("created_at"))


class Migration(migrations.Migration):
    dependencies = [
        ("news", "0007_rename_project_news_category"),
    ]

    operations = [
        migrations.AddField(
            model_name="newsarticle",
            name="published_at",
            field=models.DateTimeField(blank=True, null=True, verbose_name="发布时间"),
        ),
        migrations.AddField(
            model_name="newsarticle",
            name="view_count",
            field=models.PositiveBigIntegerField(default=0, verbose_name="浏览次数"),
        ),
        migrations.RunPython(populate_published_at, migrations.RunPython.noop),
    ]
