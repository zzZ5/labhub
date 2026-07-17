from django.db import migrations


def rename_project_category(apps, schema_editor):
    NewsCategory = apps.get_model("news", "NewsCategory")
    NewsCategory.objects.filter(slug="project-related").update(
        name="项目动态",
        description="项目立项、合作推进、阶段进展和结题信息。",
        sort_order=6,
    )


class Migration(migrations.Migration):

    dependencies = [
        ("news", "0006_add_project_news_category"),
    ]

    operations = [
        migrations.RunPython(rename_project_category, migrations.RunPython.noop),
    ]
