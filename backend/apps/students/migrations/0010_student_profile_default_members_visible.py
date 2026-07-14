from django.db import migrations, models


def normalize_student_profile_visibility(apps, schema_editor):
    StudentProfile = apps.get_model("students", "StudentProfile")
    StudentProfile.objects.filter(visibility="supervisor").update(visibility="members")


def reverse_student_profile_visibility(apps, schema_editor):
    StudentProfile = apps.get_model("students", "StudentProfile")
    StudentProfile.objects.filter(visibility="members").update(visibility="supervisor")


class Migration(migrations.Migration):
    dependencies = [
        ("students", "0009_remove_studentarchivefile_version"),
    ]

    operations = [
        migrations.AlterField(
            model_name="studentprofile",
            name="visibility",
            field=models.CharField(
                choices=[
                    ("private", "本人可见"),
                    ("supervisor", "本人/导师可见"),
                    ("pi", "硕博导师/管理员可见"),
                    ("members", "成员可见"),
                ],
                default="members",
                max_length=20,
                verbose_name="可见性",
            ),
        ),
        migrations.RunPython(normalize_student_profile_visibility, reverse_student_profile_visibility),
    ]
