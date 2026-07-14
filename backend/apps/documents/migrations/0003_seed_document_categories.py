from django.db import migrations


DOCUMENT_CATEGORIES = [
    ("lab-policy", "组内制度与通知", "实验室制度、值日安排、通知公告与常用流程。"),
    ("lab-safety", "实验室安全", "安全培训、危险源提示、废弃物处置与应急流程。"),
    ("sop", "实验方法", "实验步骤、样品前处理、质量控制和常用方法记录。"),
    ("project-admin", "项目与经费材料", "项目申报、过程管理、结题材料和经费相关模板。"),
    ("paper-writing", "论文写作与投稿", "论文模板、投稿说明、图表规范与审稿回复材料。"),
    ("seminars", "组会与学术交流", "组会汇报、文献分享、会议报告和讲座资料。"),
    ("admin-forms", "行政表格与模板", "学院、学校和课题组常用行政表格。"),
]


def seed_document_categories(apps, schema_editor):
    DocumentCategory = apps.get_model("documents", "DocumentCategory")
    for sort_order, (slug, name, description) in enumerate(DOCUMENT_CATEGORIES, start=1):
        DocumentCategory.objects.update_or_create(
            slug=slug,
            defaults={
                "name": name,
                "description": description,
                "sort_order": sort_order,
                "visibility": "members",
            },
        )


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("documents", "0002_documentversion_preview_error_and_more"),
    ]

    operations = [
        migrations.RunPython(seed_document_categories, noop_reverse),
    ]
