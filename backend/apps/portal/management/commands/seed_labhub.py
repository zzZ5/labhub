from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from django.contrib.auth import get_user_model

from apps.documents.models import Document, DocumentCategory, DocumentStatus, DocumentVersion, DocumentVisibility
from apps.instruments.models import Instrument, InstrumentCategory
from apps.members.models import Member
from apps.news.models import NewsArticle, NewsCategory, Visibility
from apps.portal.models import ContactInfo, ResearchDirection, SiteSetting
from apps.publications.models import Patent, Project, Publication
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
                "role_type": Member.RoleType.PI,
                "research_direction": "微生物生态；有机废弃物资源转化与高值产品开发",
                "email": "weiyq2019@cau.edu.cn",
                "profile": "中国农业大学资源与环境学院生态系副教授、博士、博士生导师，主要研究微生物生态与有机废弃物资源化。",
                "sort_order": 1,
                "is_public": True,
            },
        )
        for legacy_name in ["张老师", "李同学", "王同学", "陈同学", "赵同学"]:
            Member.objects.filter(name=legacy_name).update(is_public=False)

        category, _ = NewsCategory.objects.get_or_create(name="组内动态", slug="lab-news")
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

        for index in range(1, 3):
            Project.objects.update_or_create(
                title=f"农业废弃物低碳生态转化研究 {index}",
                defaults={"funding_source": "国家重点研发计划 / 国家自然科学基金", "principal_investigator": "魏雨泉", "status": "在研"},
            )
            Patent.objects.update_or_create(
                title=f"有机废弃物资源化与堆肥过程调控专利 {index}",
                defaults={"patent_number": f"CN2026{index:04d}", "inventors": "魏雨泉课题组", "status": "示例记录"},
            )

        sop_category, _ = DocumentCategory.objects.get_or_create(
            slug="sop",
            defaults={"name": "实验 SOP", "sort_order": 1, "visibility": DocumentVisibility.MEMBERS},
        )
        analysis_category, _ = DocumentCategory.objects.get_or_create(
            slug="analysis",
            defaults={"name": "数据分析教程", "sort_order": 2, "visibility": DocumentVisibility.MEMBERS},
        )
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
            (StudentArchiveFile.FileType.THESIS, "毕业论文", "v0.1"),
            (StudentArchiveFile.FileType.RAW_DATA_NOTE, "原始数据说明", "v0.1"),
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
