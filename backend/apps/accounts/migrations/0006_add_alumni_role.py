from django.db import migrations, models


ROLE_CHOICES = [
    ("member", "课题组成员"),
    ("master", "硕士生"),
    ("phd", "博士生"),
    ("undergraduate", "本科生"),
    ("alumni", "已毕业学生"),
    ("postdoc", "博士后"),
    ("instrument_manager", "仪器管理员"),
    ("document_manager", "资料管理员"),
    ("editor", "网站编辑"),
    ("pi", "硕博导师"),
    ("admin", "系统管理员"),
    ("other", "其他"),
]

PROFILE_ROLE_CHOICES = [
    ("pending", "注册待审核用户"),
    *ROLE_CHOICES,
]


def seed_alumni_role(apps, schema_editor):
    Role = apps.get_model("accounts", "Role")
    Role.objects.update_or_create(
        code="alumni",
        defaults={
            "name": "已毕业学生",
            "description": "已毕业或离组学生身份，默认不再登录内部平台。",
            "is_system": True,
        },
    )


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0005_seed_undergraduate_other_roles"),
    ]

    operations = [
        migrations.AlterField(
            model_name="role",
            name="code",
            field=models.CharField(choices=ROLE_CHOICES, max_length=64, unique=True, verbose_name="角色编码"),
        ),
        migrations.AlterField(
            model_name="userprofile",
            name="role_type",
            field=models.CharField(choices=PROFILE_ROLE_CHOICES, default="pending", max_length=32, verbose_name="主角色"),
        ),
        migrations.RunPython(seed_alumni_role, migrations.RunPython.noop),
    ]
