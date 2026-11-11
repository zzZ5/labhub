from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("wechat_articles", "0003_originalpaper")]
    operations = [migrations.AlterField(
        model_name="originalpaper", name="topic",
        field=models.CharField(blank=True, choices=[("compost", "堆肥与腐殖化"), ("soil", "土壤碳氮循环"), ("nutrients", "养分回收利用"), ("biomass", "生物质转化"), ("environment", "环境风险与减排")], max_length=20, verbose_name="专题"),
    )]
