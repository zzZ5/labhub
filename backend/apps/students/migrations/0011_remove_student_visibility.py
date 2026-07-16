from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("students", "0010_student_profile_default_members_visible"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="studentprofile",
            name="visibility",
        ),
        migrations.RemoveField(
            model_name="studentarchivefile",
            name="visibility",
        ),
    ]
