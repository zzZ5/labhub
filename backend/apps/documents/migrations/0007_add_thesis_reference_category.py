from django.db import migrations


def add_thesis_reference_category(apps, schema_editor):
    DocumentCategory = apps.get_model("documents", "DocumentCategory")
    DocumentCategory.objects.update_or_create(
        slug="thesis-reference",
        defaults={
            "name": "其他参考资料",
            "description": "学位论文、研究报告及其他科研参考资料。",
            "sort_order": 6,
        },
    )
    for sort_order, slug in enumerate(
        [
            "lab-policy",
            "lab-safety",
            "sop",
            "project-admin",
            "paper-writing",
            "thesis-reference",
            "seminars",
            "admin-forms",
        ],
        start=1,
    ):
        DocumentCategory.objects.filter(slug=slug).update(sort_order=sort_order)


def remove_thesis_reference_category(apps, schema_editor):
    DocumentCategory = apps.get_model("documents", "DocumentCategory")
    DocumentCategory.objects.filter(slug="thesis-reference").delete()


class Migration(migrations.Migration):
    dependencies = [
        ("documents", "0006_document_external_url"),
    ]

    operations = [
        migrations.RunPython(add_thesis_reference_category, remove_thesis_reference_category),
    ]
