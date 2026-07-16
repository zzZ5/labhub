from django.db import migrations, models


SYSTEM_ROLES = {
    "instrument_manager": ("仪器管理员", "维护仪器设备状态、图片、位置和使用说明。"),
    "document_manager": ("资料管理员", "上传、编辑和整理内部资料。"),
    "editor": ("网站编辑", "维护门户内容、新闻、成果和成员信息。"),
    "admin": ("系统管理员", "拥有全部系统权限。"),
}

SCHOOL_IDENTITIES = {"teacher", "pi", "postdoc", "master", "phd", "undergraduate", "other"}
LEGACY_IDENTITY_ROLES = {"member", "master", "phd", "undergraduate", "alumni", "postdoc", "other", "pi"}


def separate_identity_and_permissions(apps, schema_editor):
    UserProfile = apps.get_model("accounts", "UserProfile")
    Role = apps.get_model("accounts", "Role")
    UserRole = apps.get_model("accounts", "UserRole")

    roles = {}
    for code, (name, description) in SYSTEM_ROLES.items():
        roles[code], _ = Role.objects.update_or_create(
            code=code,
            defaults={"name": name, "description": description, "is_system": True},
        )

    for profile in UserProfile.objects.select_related("user"):
        old_value = profile.school_identity
        updates = []

        if old_value == "alumni":
            profile.school_identity = "other"
            profile.membership_status = "graduated"
            updates.extend(["school_identity", "membership_status"])
        elif old_value in SYSTEM_ROLES:
            profile.school_identity = "other"
            updates.append("school_identity")
            UserRole.objects.get_or_create(user_id=profile.user_id, role=roles[old_value])
        elif old_value not in SCHOOL_IDENTITIES:
            profile.school_identity = "other"
            updates.append("school_identity")

        if updates:
            profile.save(update_fields=list(dict.fromkeys(updates)))

    UserRole.objects.filter(role__code__in=LEGACY_IDENTITY_ROLES).delete()
    Role.objects.filter(code__in=LEGACY_IDENTITY_ROLES).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0006_add_alumni_role"),
    ]

    operations = [
        migrations.RenameField(
            model_name="userprofile",
            old_name="role_type",
            new_name="school_identity",
        ),
        migrations.AddField(
            model_name="userprofile",
            name="membership_status",
            field=models.CharField(
                choices=[("active", "在组"), ("graduated", "已毕业"), ("left", "已离组")],
                default="active",
                max_length=20,
                verbose_name="成员状态",
            ),
        ),
        migrations.AddField(
            model_name="userprofile",
            name="access_level",
            field=models.CharField(
                choices=[("full", "正常使用"), ("read_only", "只读访问")],
                default="full",
                max_length=20,
                verbose_name="访问方式",
            ),
        ),
        migrations.RunPython(separate_identity_and_permissions, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="userprofile",
            name="school_identity",
            field=models.CharField(
                choices=[
                    ("other", "其他成员"),
                    ("teacher", "教师"),
                    ("pi", "硕博导师"),
                    ("postdoc", "博士后"),
                    ("master", "硕士生"),
                    ("phd", "博士生"),
                    ("undergraduate", "本科生"),
                ],
                default="other",
                max_length=32,
                verbose_name="学校身份",
            ),
        ),
    ]
