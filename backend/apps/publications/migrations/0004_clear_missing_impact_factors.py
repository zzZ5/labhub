from django.db import migrations


def clear_missing_impact_factors(apps, schema_editor):
    publication = apps.get_model("publications", "Publication")
    publication.objects.filter(impact_factor=0).update(impact_factor=None)


class Migration(migrations.Migration):
    dependencies = [
        ("publications", "0003_alter_award_options_alter_patent_options_and_more"),
    ]

    operations = [
        migrations.RunPython(clear_missing_impact_factors, migrations.RunPython.noop),
    ]
