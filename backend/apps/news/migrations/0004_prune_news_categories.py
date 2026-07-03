from django.db import migrations


KEPT_CATEGORIES = [
    ("lab-news", "组内动态", "课题组日常动态、组会记录、师生活动与通知。"),
    ("academic-exchange", "学术交流", "学术报告、来访交流、会议参会与合作访问。"),
    ("research-progress", "科研进展", "论文发表、研究阶段进展与成果报道。"),
    ("awards", "成果荣誉", "奖励、专利、成果转化和团队荣誉信息。"),
    ("recruitment", "招生招聘", "招生信息、科研助理、博士后和访问学生招聘。"),
]
REMOVED_DEFAULT_SLUGS = ["projects", "field-work", "training", "student-development"]


def prune_news_categories(apps, schema_editor):
    NewsCategory = apps.get_model("news", "NewsCategory")
    for sort_order, (slug, name, description) in enumerate(KEPT_CATEGORIES, start=1):
        NewsCategory.objects.update_or_create(
            slug=slug,
            defaults={
                "name": name,
                "description": description,
                "sort_order": sort_order,
            },
        )
    NewsCategory.objects.filter(slug__in=REMOVED_DEFAULT_SLUGS).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("news", "0003_seed_news_categories"),
    ]

    operations = [
        migrations.RunPython(prune_news_categories, migrations.RunPython.noop),
    ]
