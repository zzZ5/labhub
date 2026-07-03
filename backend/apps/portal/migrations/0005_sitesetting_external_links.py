from django.db import migrations, models


DEFAULT_LINKS = [
    {"label": "中国农业大学", "url": "https://www.cau.edu.cn/"},
    {"label": "资源与环境学院", "url": "https://zihuan.cau.edu.cn/"},
    {"label": "教师个人主页", "url": "https://faculty.cau.edu.cn/"},
]


def seed_external_links(apps, schema_editor):
    SiteSetting = apps.get_model("portal", "SiteSetting")
    for setting in SiteSetting.objects.filter(external_links=[]):
        setting.external_links = DEFAULT_LINKS
        setting.save(update_fields=["external_links"])


class Migration(migrations.Migration):
    dependencies = [
        ("portal", "0004_researchdirection_keywords"),
    ]

    operations = [
        migrations.AddField(
            model_name="sitesetting",
            name="external_links",
            field=models.JSONField(blank=True, default=list, verbose_name="外部链接"),
        ),
        migrations.RunPython(seed_external_links, migrations.RunPython.noop),
    ]
