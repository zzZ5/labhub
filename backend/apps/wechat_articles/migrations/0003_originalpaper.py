import apps.documents.storage
import apps.wechat_articles.models
import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("wechat_articles", "0002_normalize_wechat_source_urls")]

    operations = [migrations.CreateModel(
        name="OriginalPaper",
        fields=[
            ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
            ("title", models.CharField(max_length=500, verbose_name="原文标题")),
            ("chinese_title", models.CharField(blank=True, max_length=500, verbose_name="中文标题")),
            ("authors", models.CharField(blank=True, max_length=1000, verbose_name="作者")),
            ("journal", models.CharField(blank=True, max_length=200, verbose_name="期刊")),
            ("year", models.PositiveSmallIntegerField(blank=True, null=True, verbose_name="发表年份")),
            ("doi", models.CharField(blank=True, max_length=250, null=True, unique=True, verbose_name="DOI")),
            ("topic", models.CharField(choices=[("compost", "堆肥与腐殖化"), ("soil", "土壤碳氮循环"), ("nutrients", "养分回收利用"), ("biomass", "生物质转化"), ("environment", "环境风险与减排")], max_length=20, verbose_name="专题")),
            ("publisher_url", models.URLField(blank=True, max_length=1500, verbose_name="出版社或开放获取原文链接")),
            ("wechat_url", models.URLField(blank=True, max_length=1500, verbose_name="公众号解读链接")),
            ("pdf", models.FileField(blank=True, storage=apps.documents.storage.ProtectedMediaStorage(), upload_to=apps.wechat_articles.models.original_paper_path, validators=[django.core.validators.FileExtensionValidator(["pdf"])], verbose_name="原文PDF")),
            ("sharing", models.CharField(choices=[("link_only", "仅提供原文入口"), ("open_access", "开放获取且许可允许分享"), ("authorized", "已获分享授权")], default="link_only", max_length=20, verbose_name="PDF分享方式")),
            ("rights_note", models.TextField(blank=True, verbose_name="分享许可或授权依据")),
            ("is_visible", models.BooleanField(default=False, verbose_name="公开展示")),
            ("created_at", models.DateTimeField(auto_now_add=True)),
            ("updated_at", models.DateTimeField(auto_now=True)),
        ],
        options={"ordering": ["-created_at", "-id"], "verbose_name": "论文原文", "verbose_name_plural": "论文原文"},
    )]
