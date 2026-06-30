from django.db import migrations


SYSTEM_ROLES = [
    ("member", "课题组成员", "可访问普通内部资料与仪器预约。"),
    ("master", "硕士生", "继承成员权限，可管理自己的培养档案。"),
    ("phd", "博士生", "继承成员权限，可访问更高等级实验方法资料。"),
    ("instrument_manager", "仪器管理员", "维护仪器设备状态、图片、位置和使用说明。"),
    ("document_manager", "资料管理员", "上传、编辑、归档资料与版本。"),
    ("editor", "网站编辑", "维护门户内容、新闻、成果和成员信息。"),
    ("pi", "硕博导师", "查看学生完整档案和关键项目资料。"),
    ("admin", "系统管理员", "拥有全部系统权限。"),
]


def seed_roles(apps, schema_editor):
    Role = apps.get_model("accounts", "Role")
    for code, name, description in SYSTEM_ROLES:
        Role.objects.get_or_create(code=code, defaults={"name": name, "description": description, "is_system": True})


def remove_roles(apps, schema_editor):
    Role = apps.get_model("accounts", "Role")
    Role.objects.filter(code__in=[role[0] for role in SYSTEM_ROLES], is_system=True).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(seed_roles, remove_roles),
    ]
