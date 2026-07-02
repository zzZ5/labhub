from django.db import migrations


NEWS_CATEGORIES = [
    ("lab-news", "组内动态", "课题组日常动态、组会记录、师生活动与通知。"),
    ("academic-exchange", "学术交流", "学术报告、来访交流、会议参会与合作访问。"),
    ("research-progress", "科研进展", "论文发表、研究阶段进展与成果报道。"),
    ("projects", "项目相关", "科研项目立项、推进、结题和合作进展。"),
    ("field-work", "田间试验", "田间采样、试验布设、示范应用和现场工作。"),
    ("training", "实验培训", "实验方法、仪器操作、安全规范和组内培训。"),
    ("student-development", "学生动态", "学生开题、中期、答辩、获奖和成长记录。"),
    ("awards", "成果荣誉", "奖励、专利、成果转化和团队荣誉信息。"),
    ("recruitment", "招生招聘", "招生信息、科研助理、博士后和访问学生招聘。"),
]


def seed_news_categories(apps, schema_editor):
    NewsCategory = apps.get_model("news", "NewsCategory")
    for sort_order, (slug, name, description) in enumerate(NEWS_CATEGORIES, start=1):
        NewsCategory.objects.update_or_create(
            slug=slug,
            defaults={
                "name": name,
                "description": description,
                "sort_order": sort_order,
            },
        )


class Migration(migrations.Migration):
    dependencies = [
        ("news", "0002_newsarticle_word_file"),
    ]

    operations = [
        migrations.RunPython(seed_news_categories, migrations.RunPython.noop),
    ]
