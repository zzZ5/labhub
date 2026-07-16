from django.db import migrations, models


def simplify_identity_and_status(apps, schema_editor):
    UserProfile = apps.get_model("accounts", "UserProfile")
    UserProfile.objects.filter(school_identity="teacher").update(school_identity="pi")
    UserProfile.objects.filter(membership_status__in=["graduated", "left"]).update(membership_status="former")


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0007_separate_identity_membership_permissions"),
    ]

    operations = [
        migrations.RunPython(simplify_identity_and_status, migrations.RunPython.noop),
        migrations.RemoveField(
            model_name="userprofile",
            name="access_level",
        ),
        migrations.AlterField(
            model_name="userprofile",
            name="membership_status",
            field=models.CharField(
                choices=[("active", "在组"), ("former", "已毕业/离组")],
                default="active",
                max_length=20,
                verbose_name="成员状态",
            ),
        ),
        migrations.AlterField(
            model_name="userprofile",
            name="school_identity",
            field=models.CharField(
                choices=[
                    ("pi", "硕博导师"),
                    ("postdoc", "博士后"),
                    ("phd", "博士生"),
                    ("master", "硕士生"),
                    ("undergraduate", "本科生"),
                    ("other", "其他成员"),
                ],
                default="other",
                max_length=32,
                verbose_name="学校身份",
            ),
        ),
    ]
