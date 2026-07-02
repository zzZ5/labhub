from django.db import migrations, models


LEGACY_TITLES = {
    "PI": "硕博导师",
    "teacher": "教师",
    "postdoc": "博士后",
    "phd": "博士生",
    "master": "硕士生",
    "undergraduate": "本科生",
    "alumni": "已毕业学生",
    "visitor": "访问学生",
}


def migrate_member_titles(apps, schema_editor):
    Member = apps.get_model("members", "Member")
    for member in Member.objects.all():
        updates = {}
        if member.role_type in LEGACY_TITLES:
            updates["role_type"] = LEGACY_TITLES[member.role_type]
        if not member.is_public:
            updates["sort_order"] = 0
        if updates:
            Member.objects.filter(pk=member.pk).update(**updates)


class Migration(migrations.Migration):
    dependencies = [
        ("members", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="member",
            name="role_type",
            field=models.CharField(blank=True, default="", max_length=120, verbose_name="身份头衔"),
        ),
        migrations.AlterModelOptions(
            name="member",
            options={"ordering": ["sort_order", "name"], "verbose_name": "成员", "verbose_name_plural": "成员"},
        ),
        migrations.RunPython(migrate_member_titles, migrations.RunPython.noop),
    ]
