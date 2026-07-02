from django.db import migrations


NEW_ROLES = [
    ("undergraduate", "本科生", "课题组本科生身份，可维护本人学生档案和归档资料。"),
    ("other", "其他", "其他学校身份，用于人员分类，不默认生成学生档案。"),
]


def seed_roles(apps, schema_editor):
    Role = apps.get_model("accounts", "Role")
    for code, name, description in NEW_ROLES:
        Role.objects.update_or_create(
            code=code,
            defaults={"name": name, "description": description, "is_system": True},
        )


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0004_alter_role_code_alter_userprofile_role_type"),
    ]

    operations = [
        migrations.RunPython(seed_roles, migrations.RunPython.noop),
    ]
