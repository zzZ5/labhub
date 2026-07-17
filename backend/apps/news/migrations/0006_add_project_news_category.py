from django.db import migrations


def add_project_category(apps, schema_editor):
    NewsCategory = apps.get_model("news", "NewsCategory")
    NewsCategory.objects.update_or_create(
        slug="project-related",
        defaults={
            "name": "项目相关",
            "description": "项目立项、合作推进、阶段进展和结题信息。",
            "sort_order": 6,
        },
    )


class Migration(migrations.Migration):

    dependencies = [
        ("news", "0005_newsarticle_word_html"),
    ]

    operations = [
        migrations.RunPython(add_project_category, migrations.RunPython.noop),
    ]
