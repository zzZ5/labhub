from django.db import migrations


def rename_reference_category(apps, schema_editor):
    DocumentCategory = apps.get_model("documents", "DocumentCategory")
    DocumentCategory.objects.filter(slug="thesis-reference").update(
        name="其他参考资料",
        description="学位论文、研究报告及其他科研参考资料。",
    )


class Migration(migrations.Migration):
    dependencies = [
        ("documents", "0007_add_thesis_reference_category"),
    ]

    operations = [
        migrations.RunPython(rename_reference_category, migrations.RunPython.noop),
    ]
