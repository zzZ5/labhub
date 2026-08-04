from django.db import migrations


def normalize_wechat_source_urls(apps, schema_editor):
    WechatArticle = apps.get_model("wechat_articles", "WechatArticle")
    queryset = WechatArticle.objects.filter(
        source_url__contains="/api/articles/serve-file/",
        source_guid__startswith="https://mp.weixin.qq.com/s/",
    )
    for article in queryset.iterator():
        article.source_url = article.source_guid.strip()
        article.save(update_fields=["source_url", "updated_at"])


class Migration(migrations.Migration):
    dependencies = [
        ("wechat_articles", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(normalize_wechat_source_urls, migrations.RunPython.noop),
    ]
