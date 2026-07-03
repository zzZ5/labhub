from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from django.contrib.auth import get_user_model

from apps.documents.models import Document, DocumentCategory, DocumentStatus, DocumentVersion, DocumentVisibility
from apps.instruments.models import Instrument, InstrumentCategory
from apps.members.models import Member
from apps.news.models import NewsArticle, NewsCategory, Visibility
from apps.portal.models import ContactInfo, ResearchDirection, SiteSetting
from apps.publications.models import Award, Patent, Project, Publication
from apps.students.models import StudentArchiveFile, StudentProfile, StudentVisibility


class Command(BaseCommand):
    help = "Seed LabHub public portal sample data."

    def handle(self, *args, **options):
        User = get_user_model()
        SiteSetting.objects.update_or_create(
            site_name="中农雨磷",
            defaults={
                "site_subtitle": "中国农业大学资源与环境学院",
                "description": "聚焦微生物生态、有机废弃物资源转化与高值产品开发。",
                "keywords": "中农雨磷,中国农业大学,资源与环境学院,生态系,微生物生态,有机废弃物资源化",
                "footer_text": "面向农业绿色发展与资源环境治理，开展微生物生态、有机废弃物资源转化与高值产品开发研究。",
                "contact_email": "weiyq2019@cau.edu.cn",
                "address": "中国农业大学资源与环境学院生态系，北京市海淀区圆明园西路2号中国农业大学西校区",
                "external_links": [
                    {"label": "中国农业大学", "url": "https://www.cau.edu.cn/"},
                    {"label": "资源与环境学院", "url": "https://zihuan.cau.edu.cn/"},
                    {"label": "教师个人主页", "url": "https://faculty.cau.edu.cn/"},
                ],
            },
        )
        ContactInfo.objects.update_or_create(
            title="联系我们",
            defaults={
                "content": "欢迎对微生物生态、有机废弃物资源转化与高值产品开发感兴趣的同学联系交流。",
                "email": "weiyq2019@cau.edu.cn",
                "address": "中国农业大学资源与环境学院生态系，北京市海淀区圆明园西路2号中国农业大学西校区",
            },
        )

        research_items = [
            ("微生物生态", "解析有机废弃物转化、土壤生态过程中的关键微生物群落与功能机制。"),
            ("有机废弃物资源转化", "面向农业和食品加工废弃物，研究低碳转化、稳定化和资源化利用路径。"),
            ("高值产品开发", "围绕有机肥、水溶肥和生态产品，推进从工艺优化到应用评价的转化研究。"),
            ("堆肥腐殖化调控", "研究堆肥过程中腐殖酸形成、臭气减排和品质提升的过程调控机制。"),
            ("养分循环与土壤健康", "评价有机物料还田、养分循环利用及其对土壤生态功能的影响。"),
            ("农业低碳生态转化", "服务农业废弃物低碳处理和绿色农业场景，探索可推广的技术模式。"),
        ]
        for index, (title, summary) in enumerate(
            [
                *research_items,
            ],
            start=1,
        ):
            ResearchDirection.objects.update_or_create(
                slug=f"research-{index}",
                defaults={"title": title, "summary": summary, "sort_order": index, "is_active": True},
            )

        Member.objects.update_or_create(
            name="魏雨泉",
            defaults={
                "role_type": "副教授 / 博士生导师",
                "research_direction": "微生物生态；有机废弃物资源转化与高值产品开发",
                "email": "weiyq2019@cau.edu.cn",
                "profile": "中国农业大学资源与环境学院生态系副教授、博士、博士生导师，主要研究微生物生态与有机废弃物资源化。",
                "sort_order": 1,
                "is_public": True,
            },
        )
        for legacy_name in ["张老师", "李同学", "王同学", "陈同学", "赵同学"]:
            Member.objects.filter(name=legacy_name).update(is_public=False, sort_order=0)

        news_category_specs = [
            ("组内动态", "lab-news", "课题组日常动态、组会记录、师生活动与通知。"),
            ("学术交流", "academic-exchange", "学术报告、来访交流、会议参会与合作访问。"),
            ("科研进展", "research-progress", "研究工作阶段性进展、论文发表、项目推进与成果报道。"),
            ("成果荣誉", "awards", "奖励、专利、成果转化和团队荣誉信息。"),
            ("招生招聘", "recruitment", "招生信息、科研助理、博士后和访问学生招聘。"),
        ]
        news_categories = {}
        for sort_order, (name, slug, description) in enumerate(news_category_specs, start=1):
            news_categories[slug], _ = NewsCategory.objects.update_or_create(
                slug=slug,
                defaults={"name": name, "description": description, "sort_order": sort_order},
            )
        category = news_categories["lab-news"]
        for index in range(1, 4):
            NewsArticle.objects.get_or_create(
                slug=f"news-{index}",
                defaults={
                    "title": f"实验室新闻活动 {index}",
                    "summary": "实验室公开新闻摘要。",
                    "content": "实验室公开新闻正文。",
                    "category": category,
                    "visibility": Visibility.PUBLIC,
                    "status": NewsArticle.Status.PUBLISHED,
                },
            )

        for index, publication in enumerate(
            Publication.objects.filter(title__startswith="Agricultural organic waste recycling study").order_by("year", "id"),
            start=1,
        ):
            publication.title = f"中农雨磷团队农业废弃物资源化研究方向 {index}"
            publication.authors = "中农雨磷团队"
            publication.journal = "代表性研究方向"
            publication.is_representative = True
            publication.save(update_fields=["title", "authors", "journal", "is_representative", "updated_at"])
        Publication.objects.filter(title__startswith="中农雨磷团队农业废弃物资源化研究方向").update(visibility=Visibility.ADMINS)

        latest_publications = [
            (
                "Microbial Necromass Accelerates Humic Acid Formation by Reshaping DOM Transformation Pathways During Composting",
                "Su Chang; Yi Zheng; Baoju Liu; Wenjie Chen; Yuquan Wei; Long D. Nghiem; Mohan Bai; Guochun Ding; Huike Ye; Yan Xu; Ji Li",
                "Environmental Research",
                2026,
                "AMiner ID: 69e3486a9be8eb7c4b65172e",
            ),
            (
                "Effect of Different Organic-to-inorganic Phosphorus Ratios on Organic Phosphorus Mineralization and Microbial Functions During Composting",
                "Zhen Wu; Yuquan Wei; Tong Guo; Long D. Nghiem; Zimin Wei; Yue Zhao",
                "Journal of Environmental Chemical Engineering",
                2026,
                "AMiner ID: 69f23d5b0a96f8c83c54164e",
            ),
            (
                "A Compost-Derived Functional Microbial Consortium Fortifies Humification During Bio-Organic Fertilizer Production",
                "Yang Yang; Yuxin Sun; Jiaqi Liu; Xueqing Jia; Tao Wang; Qing Chen; Yanming Li; Yuyun Wang; Zhi Xu; Yuquan Wei; Ruixue Chang",
                "Journal of Environmental Chemical Engineering",
                2026,
                "AMiner ID: 6a3ef2ee0a96f8c83c09aa02",
            ),
            (
                "Mineral-driven Accumulation of Microbial Necromass Enhanced Humification During Composting",
                "Wenjie Chen; Yan Yang; Kui Zhang; Su Chang; Yuan Chang; Ji Li; Xia Liang; Yifan Liu; Long D. Nghiem; Mohan Bai; Huike Ye; Zichao Zhao; Yuquan Wei",
                "Journal of Environmental Chemical Engineering",
                2026,
                "AMiner ID: 69cf11a29be8eb7c4bf9892d",
            ),
            (
                "The Impacts of Aeration Modes and Rates on Nitrogen Conversion and Bacterial Community Composition in a 90-M3 Silo Composting Reactor",
                "Pengxiang Xu; Shaoqi Xu; Yuquan Wei; Yongdi Liu; Sheng Hang; Yue Wang; Longli Zhang; Ji Li",
                "Environmental Technology & Innovation",
                2025,
                "AMiner ID: 686e214f163c01c850ea34d3",
            ),
            (
                "Neutral Initial pH Enhances the Formation of Humic Acid by Inhibiting the Growth of Lactobacillus in Food Waste Composting",
                "Min Xu; Yuquan Wei; Yunfeng Chen; Haibin Zhou; Shuangshuang Ma; Yabin Zhan",
                "Environmental Technology & Innovation",
                2025,
                "AMiner ID: 686e2165163c01c850ea6a69",
            ),
            (
                "Towards Data-Driven Smart Composting Techniques and Control Systems",
                "Baoju Liu; Kui Zhang; Yuquan Wei; Guochun Ding; Ting Xu; Longli Zhang; Ji Li",
                "Bioresource Technology",
                2025,
                "AMiner ID: 68f29da4163c01c8500de67d",
            ),
            (
                "Mineral-organic Composite Compost Improved Plant Growth by Ion Transporter Genes and Microbial Community Assembly Process in Degraded Soil",
                "Haimin Li; Yingjie Liu; Yuquan Wei; Kui Zhang; Baoju Liu; Zhen Wu; Yanbin Guo; Yuhan Zhang; Zhangliu Du; Ji Li",
                "Journal of Environmental Sciences",
                2026,
                "AMiner ID: 69ba749a9be8eb7c4bf3e1d2",
            ),
            (
                "Three Decades of Bio-Composted Manure Facilitate the Accrual of Plant and Microbial Biomolecules in Surface Soils",
                "Siyao Xia; Xiaoying Jin; Xiayan Liu; Xiao Wang; Ting Liao; Zhanlonggang Yu; Ji Li; Zhangliu Du",
                "Journal of Integrative Agriculture",
                2026,
                "AMiner ID: 69f1c8400a96f8c83cc5c7fa",
            ),
            (
                "Engineering Bacterial Wilt-Suppressive Compost Through Soil Microbiome Transplantation",
                "Jing Mao; Yu Shi; Zixiu Liu; Fei Wang; Yanran Zhang; Yudan Zhang; Xiaoyan Ding; Ning Wang; Ji Li; Yuquan Wei; Guochun Ding",
                "Plant and Soil",
                2025,
                "AMiner ID: 6931622e94d1bc07b4261d84",
            ),
            (
                "From Carbon Sequestration Perspective: Adsorption of Minerals Enhances the Stabilization of Organic Fractions in Composting",
                "Ziwei Jiao; Ruoqi Li; Kui Zhang; Yuhan Zhang; Yanbin Guo; Su Chang; Yuan Chang; Yuquan Wei; Zitong Kang; Yuhui Qiao; Ji Li",
                "Environmental Technology & Innovation",
                2025,
                "AMiner ID: 677d5989ae8580e7ffb580c7",
            ),
            (
                "Food Waste Used As a Resource Can Reduce Climate and Resource Burdens in Agrifood Systems",
                "Yingcheng Wang; Hao Ying; Gerald C. Shurson; Ting Chen; Zihan Wang; Yulong Yin; Huifang Zheng; Tomoaki Nakaishi; Ji Li; Zhenling Cui; Zhengxia Dou",
                "Nature Food",
                2025,
                "AMiner ID: 67d03adb163c01c85010de2c",
            ),
            (
                "Using Tree-Based Machine Learning Models to Predict Diverse Compost Maturity Via One-Hot Encoding: Model Deployment, Experimental Validation, and Practical Application",
                "Xuanshuo Zhang; Yilin Kong; Yan Yang; Yan Liu; Qianlin Gao; Ji Li; Guoxue Li; Jing Yuan",
                "Waste Management",
                2025,
                "AMiner ID: 686c25f4163c01c850d601d0",
            ),
            (
                "Continuously Applying Kitchen Waste Fertiliser More Strongly Promotes Microbial-Derived Carbon Accumulation in Mineral-Associated Organic Carbon Than Other Fertilisers Across the Paddy Soil Profile in the Yangtze River Delta, China",
                "Jiaqian Gao; Jieming Li; Fan Wang; Ji Li",
                "Soil & Tillage Research",
                2025,
                "AMiner ID: 686e5078163c01c85044d558",
            ),
            (
                "Changes of Bacterial Necromass and Their Roles in Humus Conversion During Organic Wastes Composting from Different Sources",
                "Wenjie Chen; Yan Yang; Su Chang; Yuquan Wei; Zhen Wu; Kaiyan Tang; Yuan Chang; Yifan Zhang; Ji Li; Ting Xu; Xia Liang",
                "Bioresource Technology",
                2025,
                "AMiner ID: 672736b801d2a3fbfcff825d",
            ),
            (
                "Mature Compost Enhanced the Harmlessness Level in Co-Composting Swine Manure and Carcasses in Large-Scale Silo Reactors",
                "Ziwei Jiao; Liping Zhang; Ake Zhang; Ruoqi Li; Kui Zhang; Zhen Wu; Zitong Kang; Yuquan Wei; Longli Zhang; Yue Wang; Xiong Shi; Ji Li",
                "Frontiers in Microbiology",
                2024,
                "AMiner ID: 67345a5c01d2a3fbfc2257e3",
            ),
        ]
        for sort_order, (title, authors, journal, year, abstract) in enumerate(latest_publications, start=1):
            Publication.objects.update_or_create(
                title=title,
                defaults={
                    "authors": authors,
                    "journal": journal,
                    "year": year,
                    "abstract": abstract,
                    "visibility": Visibility.PUBLIC,
                    "is_representative": False,
                    "sort_order": sort_order,
                },
            )

        publication_dois = {
            "Microbial Necromass Accelerates Humic Acid Formation by Reshaping DOM Transformation Pathways During Composting": "10.1016/j.envres.2026.124536",
            "Effect of Different Organic-to-inorganic Phosphorus Ratios on Organic Phosphorus Mineralization and Microbial Functions During Composting": "10.1016/j.jece.2026.122925",
            "A Compost-Derived Functional Microbial Consortium Fortifies Humification During Bio-Organic Fertilizer Production": "10.1016/j.jece.2026.123765",
            "Mineral-driven Accumulation of Microbial Necromass Enhanced Humification During Composting": "10.1016/j.jece.2026.122517",
            "The Impacts of Aeration Modes and Rates on Nitrogen Conversion and Bacterial Community Composition in a 90-M3 Silo Composting Reactor": "10.1016/j.eti.2025.104265",
            "Neutral Initial pH Enhances the Formation of Humic Acid by Inhibiting the Growth of Lactobacillus in Food Waste Composting": "10.1016/j.eti.2025.104271",
            "Towards Data-Driven Smart Composting Techniques and Control Systems": "10.1016/j.biortech.2025.133514",
            "Mineral-organic Composite Compost Improved Plant Growth by Ion Transporter Genes and Microbial Community Assembly Process in Degraded Soil": "10.1016/j.jes.2026.03.003",
            "Three Decades of Bio-Composted Manure Facilitate the Accrual of Plant and Microbial Biomolecules in Surface Soils": "10.1016/j.jia.2026.04.039",
            "From Carbon Sequestration Perspective: Adsorption of Minerals Enhances the Stabilization of Organic Fractions in Composting": "10.1016/j.eti.2025.104023",
            "Food Waste Used As a Resource Can Reduce Climate and Resource Burdens in Agrifood Systems": "10.1038/s43016-025-01140-z",
            "Using Tree-Based Machine Learning Models to Predict Diverse Compost Maturity Via One-Hot Encoding: Model Deployment, Experimental Validation, and Practical Application": "10.1016/j.wasman.2025.114981",
            "Continuously Applying Kitchen Waste Fertiliser More Strongly Promotes Microbial-Derived Carbon Accumulation in Mineral-Associated Organic Carbon Than Other Fertilisers Across the Paddy Soil Profile in the Yangtze River Delta, China": "10.1016/j.still.2025.106614",
            "Changes of Bacterial Necromass and Their Roles in Humus Conversion During Organic Wastes Composting from Different Sources": "10.1016/j.biortech.2024.131740",
            "Mature Compost Enhanced the Harmlessness Level in Co-Composting Swine Manure and Carcasses in Large-Scale Silo Reactors": "10.3389/fmicb.2024.1494332",
        }
        for title, doi in publication_dois.items():
            Publication.objects.filter(title=title).update(doi=doi)

        detailed_publications = [
            {
                "title": "Recycling of nutrients from organic waste by advanced compost technology-A case study",
                "authors": "Yuquan Wei; Nan Wang; Yufeng Lin; Yabin Zhan; Xiaoyan Ding; Yongdi Liu; Ake Zhang; Guochun Ding; Ting Xu; Ji Li",
                "journal": "Bioresource Technology",
                "year": 2021,
                "doi": "10.1016/j.biortech.2021.125411",
                "abstract": "This paper reports a case study on advanced composting for nutrient recovery from organic waste, focusing on process control, product quality and resource recycling pathways.",
            },
            {
                "title": "Impact of inoculation and turning for full-scale composting on core bacterial community and their co-occurrence compared by network analysis",
                "authors": "Bo Wang; Yue Wang; Yuquan Wei; Wenjie Chen; Guochun Ding; Yabin Zhan; Yongdi Liu; Ting Xu; Jianjun Xiao; Ji Li",
                "journal": "Bioresource Technology",
                "year": 2022,
                "doi": "10.1016/j.biortech.2021.126417",
                "abstract": "The study evaluates inoculation and turning strategies in full-scale composting and uses microbial network analysis to reveal how engineering operations reshape core bacterial communities.",
            },
            {
                "title": "Inoculation of phosphate-solubilizing bacteria (Bacillus) regulates microbial interaction to improve phosphorus fractions mobilization during kitchen waste composting",
                "authors": "Xuejun Zhang; Yabin Zhan; Hao Zhang; Ronghua Wang; Xiaoli Tao; Liping Zhang; Yilin Zuo; Lei Zhang; Yuquan Wei; Ji Li",
                "journal": "Bioresource Technology",
                "year": 2021,
                "doi": "10.1016/j.biortech.2021.125714",
                "abstract": "The work investigates Bacillus inoculation during kitchen waste composting and explains how phosphate-solubilizing bacteria regulate microbial interactions and phosphorus mobilization.",
            },
            {
                "title": "Organic carbon sequestration in Chinese croplands under compost application and its contribution to carbon neutrality",
                "authors": "Zhaoxin Chen; Yuquan Wei; Zhiye Zhang; Guang'an Wang; Ji Li",
                "journal": "Environmental Science and Pollution Research",
                "year": 2022,
                "doi": "",
                "abstract": "This study assesses the carbon sequestration potential of compost application in Chinese croplands and discusses its contribution to agricultural carbon neutrality.",
            },
            {
                "title": "Effects of different C/N ratios on the maturity and microbial quantity of composting with sesame meal and rice straw biochar",
                "authors": "Yabin Zhan; Yuquan Wei; Zhiye Zhang; Ake Zhang; Yanbao Li; Ji Li",
                "journal": "Biochar",
                "year": 2021,
                "doi": "",
                "abstract": "The paper compares composting systems with different carbon-nitrogen ratios and biochar amendment, linking maturity indicators with microbial quantity changes.",
            },
            {
                "title": "Tomato microbiome under long-term organic and conventional farming",
                "authors": "Zhiye Zhang; Yousheng Xiao; Yabin Zhan; Zhiqing Zhang; Zhen Liu; Yuquan Wei; Ting Xu; Ji Li",
                "journal": "iMeta",
                "year": 2022,
                "doi": "10.1002/imt2.48",
                "abstract": "The article compares tomato microbiomes under long-term organic and conventional farming systems, supporting the team's long-term organic agriculture research line.",
            },
            {
                "title": "Insights into bacterial diversity in compost: Core microbiome and prevalence of potential pathogenic bacteria",
                "authors": "Yue Wang; Jingyi Gong; Jiaxin Li; Yinyin Xin; Ziyu Hao; Chen Chen; Hongxing Li; Bo Wang; Min Ding; Weiwei Li; Ziyue Zhang; Pengxiang Xu; Ting Xu; Guochun Ding; Ji Li",
                "journal": "Science of the Total Environment",
                "year": 2020,
                "doi": "10.1016/j.scitotenv.2020.137304",
                "abstract": "This paper characterizes bacterial diversity and the core microbiome in compost, with attention to the prevalence of potentially pathogenic bacteria during composting.",
            },
            {
                "title": "Towards the circular nitrogen economy-A global meta-analysis of composting technologies reveals much potential for mitigating nitrogen losses",
                "authors": "Shuxin Zhao; Stephan Schmidt; Weidong Qin; Ji Li; Guoxue Li; Fusuo Zhang",
                "journal": "Science of the Total Environment",
                "year": 2020,
                "doi": "10.1016/j.scitotenv.2019.135401",
                "abstract": "A global meta-analysis quantifies the nitrogen-loss mitigation potential of composting technologies and frames composting as an important pathway for circular nitrogen management.",
            },
            {
                "title": "Dynamics of oxytetracycline and resistance genes in soil under long-term intensive compost fertilization in northern China",
                "authors": "Ming Wu; Hui Han; Xin Zheng; Mohan Bai; Ting Xu; Guochun Ding; Ji Li",
                "journal": "Environmental Science and Pollution Research",
                "year": 2019,
                "doi": "",
                "abstract": "The study tracks oxytetracycline and resistance genes in soils receiving long-term intensive compost fertilization, providing evidence for risk assessment of organic amendments.",
            },
            {
                "title": "外源添加剂对富磷餐厨废弃物堆肥磷素活化的影响",
                "authors": "魏雨泉; 李季",
                "journal": "环境工程",
                "year": 2022,
                "doi": "10.13205/j.hjgc.202210015",
                "abstract": "研究外源添加剂对富磷餐厨废弃物堆肥过程中磷素形态转化和有效性提升的影响，为餐厨废弃物资源化提供技术依据。",
            },
            {
                "title": "通风条件对餐厨废弃物辅热生物干化过程硫素转化的影响",
                "authors": "魏雨泉; 李季",
                "journal": "农业工程学报",
                "year": 2022,
                "doi": "10.11975/j.issn.1002-6819.2022.z.033",
                "abstract": "论文围绕餐厨废弃物辅热生物干化过程，分析通风条件对硫素转化与过程调控的影响。",
            },
            {
                "title": "功能菌接种对石油污染土壤修复效果及微生物群落的影响",
                "authors": "左一琳; 陈文杰; 孙慧杰; 丁晓艳; 詹亚斌; 张昊; 丁国春; 李季; 魏雨泉; 刘蕊",
                "journal": "环境工程技术学报",
                "year": 2023,
                "doi": "10.12153/j.issn.1674-991X.20230177",
                "abstract": "研究功能菌接种对石油污染土壤修复效果和微生物群落变化的影响，体现团队在污染生态修复方向的研究积累。",
            },
            {
                "title": "基于Meta分析研究菌剂添加对堆肥产品中氮含量的影响",
                "authors": "王越; 丁晓艳; 王博; 薛衔乐; 苟洪城; 蒋正波; 魏雨泉; 丁国春; 李季",
                "journal": "农业工程学报",
                "year": 2024,
                "doi": "",
                "abstract": "基于 Meta 分析评估菌剂添加对堆肥产品氮含量的影响，为堆肥过程氮素保持和产品质量提升提供综合证据。",
            },
            {
                "title": "我国畜禽养殖粪污资源化利用装备现状与展望",
                "authors": "张英慧; 刘旭杰; 李季; 王博; 许艇; 苏敬; 魏雨泉; 张奎",
                "journal": "中国农业大学学报",
                "year": 2024,
                "doi": "",
                "abstract": "文章梳理我国畜禽养殖粪污资源化利用装备发展现状与趋势，为团队工程装备和平台建设提供背景支撑。",
            },
            {
                "title": "翻堆频率对餐厨废弃物生物干化-好氧发酵细菌群落结构的影响",
                "authors": "张宇丹; 罗越坚; 李琬婷; 李若琪; 张陇利; 丁国春; 魏雨泉; 许艇; 李季",
                "journal": "中国农业大学学报",
                "year": 2025,
                "doi": "",
                "abstract": "论文分析翻堆频率对餐厨废弃物生物干化-好氧发酵过程中细菌群落结构的影响，服务于工艺参数优化。",
            },
        ]
        base_order = len(latest_publications)
        for offset, paper in enumerate(detailed_publications, start=1):
            Publication.objects.update_or_create(
                title=paper["title"],
                defaults={
                    "authors": paper["authors"],
                    "journal": paper["journal"],
                    "year": paper["year"],
                    "doi": paper["doi"],
                    "abstract": paper["abstract"],
                    "visibility": Visibility.PUBLIC,
                    "is_representative": False,
                    "sort_order": base_order + offset,
                },
            )

        Project.objects.filter(title__startswith="农业生态环境项目").delete()
        Project.objects.filter(title__startswith="农业废弃物低碳生态转化研究").delete()
        Patent.objects.filter(title__startswith="智能堆肥调控专利").delete()
        Patent.objects.filter(title__startswith="有机废弃物资源化与堆肥过程调控专利").delete()

        public_projects = [
            ("城乡有机废弃物高效快速堆肥关键技术与设备研发及应用", "国家/行业科技成果与工程应用", "李季、魏雨泉团队", "持续推广"),
            ("环太湖城乡有机废弃物处理利用示范区建设", "区域有机循环示范工程", "李季团队", "示范应用"),
            ("有机废弃物资源化与智能堆肥过程调控研究", "国家级/省部级科研项目", "中农雨磷团队", "在研"),
            ("有机肥长期定位试验与土壤健康提升研究", "长期定位试验与团队持续研究", "李季团队", "持续开展"),
            ("农业有机废弃物腐殖化与养分循环机制研究", "基础研究与青年人才项目", "魏雨泉团队", "在研"),
            ("中国农大-企业有机资源循环利用产学研合作", "产学研合作项目", "李季、魏雨泉团队", "持续合作"),
        ]
        for title, source, pi, status_label in public_projects:
            Project.objects.update_or_create(
                title=title,
                defaults={
                    "funding_source": source,
                    "principal_investigator": pi,
                    "status": status_label,
                    "visibility": Visibility.PUBLIC,
                    "description": "门户展示版，仅展示项目方向、合作类型和推进状态。",
                },
            )

        detailed_projects = [
            {
                "title": "城乡有机废弃物高效快速堆肥关键技术与设备研发及应用",
                "project_number": "HJJS-2023-1-09",
                "funding_source": "中国环保产业协会环境技术进步奖成果",
                "principal_investigator": "李季、魏雨泉团队",
                "status": "一等奖 / 持续推广",
                "description": "围绕城乡有机废弃物快速堆肥、工程装备和规模化应用形成的综合技术成果，门户展示仅保留公开编号与成果方向。",
            },
            {
                "title": "规模化养殖场固体废弃物生物处理技术与示范",
                "project_number": "2007-2015-示范项目",
                "funding_source": "长期示范与工程应用项目",
                "principal_investigator": "李季团队",
                "status": "已完成",
                "description": "面向规模化养殖场固体废弃物资源化处理，开展生物处理技术和工程示范。",
            },
            {
                "title": "《有机肥料安全风险评价技术规范》标准制定",
                "project_number": "2021-部委科技项目",
                "funding_source": "国家部委其他科技项目",
                "principal_investigator": "李季团队",
                "status": "已完成",
                "description": "围绕有机肥料安全风险评价开展技术规范制定与支撑研究。",
            },
            {
                "title": "餐厨垃圾沼渣好氧堆肥及有机肥生产技术",
                "project_number": "2020-企业委托",
                "funding_source": "企业单位委托科技项目",
                "principal_investigator": "李季团队",
                "status": "已完成",
                "description": "面向餐厨垃圾沼渣好氧堆肥和有机肥生产过程，开展工艺优化和应用研究。",
            },
            {
                "title": "功能有机肥及高效水溶肥研发",
                "project_number": "2024-企业委托",
                "funding_source": "企业单位委托科技项目",
                "principal_investigator": "李季团队",
                "status": "在研",
                "description": "围绕功能有机肥和高效水溶肥产品开发开展产学研合作研究。",
            },
            {
                "title": "全国畜禽粪肥生产与使用情况调查评估",
                "project_number": "2025-事业单位委托",
                "funding_source": "事业单位委托科技项目",
                "principal_investigator": "李季团队",
                "status": "在研",
                "description": "开展畜禽粪肥生产与使用情况调查评估，为资源化利用和管理决策提供数据支撑。",
            },
            {
                "title": "清废兴源--城乡有机循环建设者",
                "project_number": "2023-2025-双创项目",
                "funding_source": "学生创新创业与成果转化培育",
                "principal_investigator": "魏雨泉、李季指导团队",
                "status": "持续培育",
                "description": "依托团队有机废弃物资源化研究基础开展学生创新创业训练和成果转化培育。",
            },
        ]
        for project in detailed_projects:
            Project.objects.update_or_create(
                title=project["title"],
                defaults={
                    "project_number": project["project_number"],
                    "funding_source": project["funding_source"],
                    "principal_investigator": project["principal_investigator"],
                    "status": project["status"],
                    "visibility": Visibility.PUBLIC,
                    "description": project["description"],
                },
            )

        public_patents = [
            ("一株普里斯特氏菌 Y3 及其应用", "2025109306773", "魏雨泉; 方雯瑄; 罗妍; 常素; 蒋正波; 李季; 许艇", "申请中"),
            ("一种堆肥高效促腐菌剂及其制备方法和应用", "CN202510585240.0", "罗肖丽; 李俊; 许艇; 王天舒; 魏雨泉; 关大伟; 李力; 廖斌斌", "授权"),
            ("一种生物干化分段式曝气的方法", "ZL202010584395.X", "李季; 詹亚斌; 魏雨泉; 张阿克", "授权"),
            ("堆肥反应器", "ZL202020730292.5", "李季; 籍延宝; 魏雨泉; 詹亚斌; 吴明; 吴凌彦", "实用新型"),
            ("一种可降解二苯并噻吩的菌株及其生产的菌液和应用", "CN202210791897.9", "魏雨泉; 左一琳; 张阿克; 李季; 丁国春; 张奎; 丁晓艳", "公开"),
            ("一种通过生物聚磷制备的富磷高效堆肥产品及其方法", "ZL201710028415.3", "赵越; 魏雨泉; 魏自民; 贾立明; 董英莉; 李艳杰", "授权"),
            ("一种基于最大供磷力的堆肥施用方法", "ZL201610255590.1", "赵越; 魏雨泉; 魏自民; 卢倩; 王雪芹; 曹振宇; 崔洪洋; 赵艺; 刘海龙", "授权"),
            ("一种有机废弃物冬季发酵的生物能源保温方法", "ZL201510271409.1", "魏自民; 王雪芹; 赵越; 张旭; 魏雨泉; 赵昕宇", "授权"),
            ("可导气圆柱体立式土壤矿化速率测定装置", "ZL201410366078.5", "魏自民; 张旭; 赵越; 魏雨泉; 赵昕宇; 时俭红", "授权"),
            ("一种基于微生物网络评估环境污染风险的方法", "ZL201910032923.8", "张芳; 魏雨泉; 李广贺; 张昊; 郑迪; 张旭", "授权"),
        ]
        for title, number, inventors, status_label in public_patents:
            Patent.objects.update_or_create(
                title=title,
                defaults={
                    "patent_number": number,
                    "inventors": inventors,
                    "status": status_label,
                    "visibility": Visibility.PUBLIC,
                },
            )

        detailed_patents = [
            ("一种基于微生物降解耦合电化学法的氯代烃污染地下水处理装置和修复方法", "ZL201910031458.6", "张芳; 魏雨泉; 李广贺; 袁英; 耿竹凝; 张旭", "授权"),
            ("一种河流、湖泊沉积物重金属生态毒性风险的综合评价方法", "ZL201910364910.0", "张芳; 魏雨泉; 李广贺; 张昊; 赵嬴双; 张旭", "授权"),
            ("一种用于监测沉积物速效磷负荷污染的特异性引物", "ZL201910363294.7", "张芳; 魏雨泉; 李广贺; 袁英; 刘顿; 张旭", "授权"),
            ("一种用于扩增嗜冷杆菌属的特异性引物", "ZL201410369525.2", "赵越; 王佰洁; 魏自民; 赵昕宇; 张旭; 魏雨泉; 王雪芹", "授权"),
        ]
        for title, number, inventors, status_label in detailed_patents:
            Patent.objects.update_or_create(
                title=title,
                defaults={
                    "patent_number": number,
                    "inventors": inventors,
                    "status": status_label,
                    "visibility": Visibility.PUBLIC,
                },
            )

        public_awards = [
            {
                "title": "城乡有机废弃物高效快速堆肥关键技术与设备研发及应用",
                "award_level": "2023 年环境技术进步奖一等奖",
                "award_date": "2023-12-01",
                "participants": "李季; 韩跃国; 魏雨泉等",
                "description": "围绕城乡有机废弃物快速堆肥关键技术、装备研发与工程应用形成的公开成果奖励。",
            },
            {
                "title": "清废兴源--城乡有机循环建设者",
                "award_level": "2023 年中国国际大学生创新大赛国家金奖",
                "award_date": "2023-11-01",
                "participants": "指导教师：魏雨泉",
                "description": "依托团队有机废弃物资源化和城乡有机循环方向形成的学生创新创业成果。",
            },
            {
                "title": "清废兴源--城乡有机循环建设者",
                "award_level": "2023 年北京赛区一等奖",
                "award_date": "2023-08-01",
                "participants": "指导教师：魏雨泉",
                "description": "学生创新创业项目在北京赛区获得一等奖。",
            },
            {
                "title": "有机废弃物资源化与双碳创新实践",
                "award_level": "2023 年中国研究生“双碳”创新与创意大赛二等奖",
                "award_date": "2023-10-01",
                "participants": "指导教师：李季; 魏雨泉",
                "description": "围绕有机废弃物资源化、低碳循环和农业生态环境治理开展的研究生创新实践。",
            },
            {
                "title": "城乡有机循环与资源化利用创新实践",
                "award_level": "2024 年青创北京挑战杯金奖",
                "award_date": "2024-06-01",
                "participants": "指导教师：魏雨泉; 李季; 李辕",
                "description": "面向城乡有机循环建设和资源化利用场景的创新实践成果。",
            },
            {
                "title": "有机废弃物资源化创新创业项目",
                "award_level": "2025 年北京大学生创新创业大赛一等奖 / 金种子项目",
                "award_date": "2025-06-01",
                "participants": "指导教师：魏雨泉; 李季",
                "description": "依托中农雨磷团队研究基础开展的学生创新创业项目。",
            },
        ]
        for award in public_awards:
            Award.objects.update_or_create(
                title=award["title"],
                award_level=award["award_level"],
                defaults={
                    "award_date": award["award_date"],
                    "participants": award["participants"],
                    "description": award["description"],
                    "visibility": Visibility.PUBLIC,
                },
            )

        document_category_specs = [
            ("组内制度与通知", "lab-policy", "实验室制度、值日安排、通知公告与常用流程。"),
            ("实验室安全", "lab-safety", "安全培训、危险源提示、废弃物处置与应急流程。"),
            ("实验方法与 SOP", "sop", "仪器操作、样品前处理、实验步骤与质量控制。"),
            ("仪器设备资料", "instrument-docs", "仪器说明书、维护记录、操作说明和配套软件。"),
            ("数据与代码规范", "data-code", "数据模板、统计分析、绘图规范与代码归档要求。"),
            ("项目与经费材料", "project-admin", "项目申报、过程管理、结题材料和经费相关模板。"),
            ("论文写作与投稿", "paper-writing", "论文模板、投稿说明、图表规范与回复审稿材料。"),
            ("组会与学术交流", "seminars", "组会汇报、文献分享、会议报告和讲座资料。"),
            ("学生资料模板", "student-templates", "开题、中期、答辩、毕业归档等学生常用模板。"),
            ("行政表格与模板", "admin-forms", "学院、学校和课题组常用行政表格。"),
        ]
        document_categories = {}
        for sort_order, (name, slug, description) in enumerate(document_category_specs, start=1):
            document_categories[slug], _ = DocumentCategory.objects.update_or_create(
                slug=slug,
                defaults={
                    "name": name,
                    "description": description,
                    "sort_order": sort_order,
                    "visibility": DocumentVisibility.MEMBERS,
                },
            )
        sop_category = document_categories["sop"]
        analysis_category = document_categories["data-code"]
        sample_documents = [
            ("堆肥反应器操作 SOP", sop_category, "v1.3", "包含开机检查、温度控制、通风参数、采样记录和安全注意事项。"),
            ("腐殖酸组分测定流程", sop_category, "v2.0", "说明样品前处理、提取步骤、质量控制和数据记录模板。"),
            ("堆肥气体采样数据整理模板", analysis_category, "v1.1", "用于田间和反应器气体采样数据整理的统一模板。"),
        ]
        for title, category, version, description in sample_documents:
            document, _ = Document.objects.get_or_create(
                title=title,
                defaults={
                    "category": category,
                    "description": description,
                    "visibility": DocumentVisibility.MEMBERS,
                    "status": DocumentStatus.ACTIVE,
                    "allow_download": True,
                },
            )
            if not document.versions.exists():
                DocumentVersion.objects.create(
                    document=document,
                    version=version,
                    file=ContentFile(f"{title}\n{description}\n".encode("utf-8"), name=f"{document.id}_{version}.txt"),
                    original_filename=f"{title}.txt",
                    change_log="示例资料初始化版本。",
                    is_current=True,
                    file_type="text/plain",
                )

        instrument_category, _ = InstrumentCategory.objects.get_or_create(
            slug="compost-platform",
            defaults={"name": "堆肥与环境分析平台", "sort_order": 1},
        )
        for index, (name, room, need_training, status) in enumerate(
            [
                ("智能堆肥反应器", "生态过程实验室 A201", False, Instrument.Status.NORMAL),
                ("总有机碳分析仪", "环境样品分析室 B112", True, Instrument.Status.NORMAL),
                ("气体采样与监测系统", "田间试验平台", True, Instrument.Status.MAINTENANCE),
            ],
            start=1,
        ):
            Instrument.objects.get_or_create(
                name=name,
                defaults={
                    "category": instrument_category,
                    "room": room,
                    "status": status,
                    "need_training": need_training,
                    "sort_order": index,
                },
            )

        pi_user, _ = User.objects.get_or_create(username="pi_demo", defaults={"email": "pi@example.com", "first_name": "张老师"})
        pi_user.profile.real_name = "张老师"
        pi_user.profile.is_approved = True
        pi_user.profile.save()
        student_user, _ = User.objects.get_or_create(username="student_demo", defaults={"email": "student@example.com", "first_name": "李同学"})
        student_user.profile.real_name = "李同学"
        student_user.profile.is_approved = True
        student_user.profile.save()
        student, _ = StudentProfile.objects.get_or_create(
            user=student_user,
            defaults={
                "name": "李同学",
                "degree_type": StudentProfile.DegreeType.PHD,
                "grade": "2023级",
                "supervisor": pi_user,
                "research_topic": "智能堆肥过程建模与腐殖化调控",
                "research_direction": "智能堆肥与过程建模",
                "visibility": StudentVisibility.SUPERVISOR,
            },
        )
        for file_type, title, version in [
            (StudentArchiveFile.FileType.PROPOSAL_REPORT, "开题报告", "v1.0"),
            (StudentArchiveFile.FileType.PROPOSAL_PPT, "开题 PPT", "v1.0"),
            (StudentArchiveFile.FileType.MIDTERM_REPORT, "中期报告", "v1.0"),
            (StudentArchiveFile.FileType.MIDTERM_PPT, "中期 PPT", "v1.0"),
            (StudentArchiveFile.FileType.THESIS, "毕业论文", "v0.1"),
            (StudentArchiveFile.FileType.DEFENSE_PPT, "答辩 PPT", "v1.0"),
            (StudentArchiveFile.FileType.PAPER, "发表论文", "v0.1"),
            (StudentArchiveFile.FileType.OTHER, "其它材料", "v1.0"),
        ]:
            if not StudentArchiveFile.objects.filter(student=student, file_type=file_type, title=title).exists():
                StudentArchiveFile.objects.create(
                    student=student,
                    file_type=file_type,
                    title=title,
                    file=ContentFile(f"{title} 示例内容\n".encode("utf-8"), name=f"{student.id}_{file_type}.txt"),
                    version=version,
                    visibility=StudentVisibility.SUPERVISOR,
                    uploaded_by=student_user,
                    description="示例学生归档资料。",
                )

        self.stdout.write(self.style.SUCCESS("LabHub sample public data seeded."))
