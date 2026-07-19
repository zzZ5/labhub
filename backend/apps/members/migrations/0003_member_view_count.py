from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("members", "0002_member_title_and_sort_visibility")]

    operations = [
        migrations.AddField(
            model_name="member",
            name="view_count",
            field=models.PositiveIntegerField(default=0, verbose_name="浏览次数"),
        ),
    ]
