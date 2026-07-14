from django.db import migrations


def refine_document_categories(apps, schema_editor):
    DocumentCategory = apps.get_model("documents", "DocumentCategory")

    DocumentCategory.objects.update_or_create(
        slug="sop",
        defaults={
            "name": "实验方法",
            "description": "实验步骤、样品前处理、质量控制和常用方法记录。",
            "sort_order": 3,
            "visibility": "members",
        },
    )
    DocumentCategory.objects.filter(slug__in=["instrument-docs", "student-templates", "testing-service", "data-code"]).delete()

    for sort_order, slug in enumerate(
        [
            "lab-policy",
            "lab-safety",
            "sop",
            "project-admin",
            "paper-writing",
            "seminars",
            "admin-forms",
        ],
        start=1,
    ):
        DocumentCategory.objects.filter(slug=slug).update(sort_order=sort_order)


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):
    dependencies = [
        ("documents", "0003_seed_document_categories"),
    ]

    operations = [
        migrations.RunPython(refine_document_categories, noop_reverse),
    ]
