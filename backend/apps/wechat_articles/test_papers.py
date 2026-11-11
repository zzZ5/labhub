from tempfile import TemporaryDirectory
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.files.storage import FileSystemStorage
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from rest_framework.test import APIClient
from apps.accounts.models import Role, RoleCode, UserRole

from .models import OriginalPaper
from .paper_metadata import MetadataError


class OriginalPaperTests(TestCase):
    def setUp(self):
        directory = TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        field = OriginalPaper._meta.get_field("pdf")
        old_storage = field.storage
        field.storage = FileSystemStorage(location=directory.name)
        self.addCleanup(setattr, field, "storage", old_storage)
        self.public = APIClient()
        self.manager = APIClient()
        self.manager.force_authenticate(get_user_model().objects.create_superuser("paper-admin", "admin@example.com", "test"))

    def payload(self, **kwargs):
        return {"title": "Composting and nutrient recovery", "chinese_title": "堆肥养分回收",
                "topic": "compost", "doi": "10.1234/test", **kwargs}

    def upload(self, **kwargs):
        return self.manager.post("/api/wechat/manage/papers/", self.payload(
            pdf=SimpleUploadedFile("paper.pdf", b"%PDF-1.4\n%%EOF", "application/pdf"), **kwargs,
        ), format="multipart")

    def test_upload_defaults_to_hidden_and_never_exposes_storage_path(self):
        response = self.upload()
        self.assertEqual(response.status_code, 201, response.data)
        self.assertTrue(response.data["has_pdf"])
        self.assertNotIn("pdf", response.data)
        self.assertFalse(response.data["is_visible"])
        self.assertEqual(response.data["preview_url"], "")
        self.assertEqual(self.public.get("/api/wechat/papers/").data["count"], 0)
        self.assertEqual(self.public.get(f'/api/wechat/papers/{response.data["id"]}/download/').status_code, 404)

    def test_link_only_paper_can_be_listed_but_file_is_not_public(self):
        response = self.upload(is_visible=True)
        pk = response.data["id"]
        detail = self.public.get(f"/api/wechat/papers/{pk}/")
        self.assertEqual(detail.status_code, 200)
        self.assertNotIn("rights_note", detail.data)
        self.assertNotIn("has_pdf", detail.data)
        self.assertEqual(detail.data["download_url"], "")
        self.assertEqual(self.public.get(f"/api/wechat/papers/{pk}/preview/").status_code, 404)

    def test_public_preview_download_and_revocation(self):
        response = self.upload(is_visible=True, sharing="open_access", rights_note="CC BY 4.0; publisher permission page")
        self.assertEqual(response.status_code, 201, response.data)
        pk = response.data["id"]
        for action, disposition in [("preview", "inline"), ("download", "attachment")]:
            result = self.public.get(f"/api/wechat/papers/{pk}/{action}/")
            self.assertEqual(result.status_code, 200)
            self.assertEqual(result["Content-Type"], "application/pdf")
            self.assertTrue(result["Content-Disposition"].startswith(disposition))
            self.assertEqual(result["Cache-Control"], "no-store")
            self.assertTrue(b"".join(result.streaming_content).startswith(b"%PDF-"))
            result.close()
        self.manager.patch(f"/api/wechat/manage/papers/{pk}/", {"sharing": "link_only"}, format="json")
        self.assertEqual(self.public.get(f"/api/wechat/papers/{pk}/download/").status_code, 404)

    def test_hiding_shared_paper_immediately_blocks_detail_and_download(self):
        response = self.upload(is_visible=True, sharing="authorized", rights_note="Author permission")
        pk = response.data["id"]
        self.manager.patch(f"/api/wechat/manage/papers/{pk}/", {"is_visible": False}, format="json")
        for action in ["", "preview/", "download/"]:
            self.assertEqual(self.public.get(f"/api/wechat/papers/{pk}/{action}").status_code, 404)

    def test_sharing_requires_permission_basis(self):
        response = self.upload(sharing="open_access")
        self.assertEqual(response.status_code, 400)
        self.assertIn("rights_note", response.data)

    def test_invalid_file_is_rejected(self):
        for name, content in [("bad.pdf", b"<html>bad</html>"), ("bad.txt", b"%PDF-1.4")]:
            response = self.manager.post("/api/wechat/manage/papers/", self.payload(
                pdf=SimpleUploadedFile(name, content),
            ), format="multipart")
            self.assertEqual(response.status_code, 400)
            self.assertIn("pdf", response.data)

    def test_normalized_doi_is_unique_and_blank_dois_are_allowed(self):
        first = self.manager.post("/api/wechat/manage/papers/", self.payload(doi="https://doi.org/10.1234/TEST"), format="json")
        self.assertEqual(first.status_code, 201, first.data)
        self.assertEqual(first.data["doi"], "10.1234/test")
        duplicate = self.manager.post("/api/wechat/manage/papers/", self.payload(), format="json")
        self.assertEqual(duplicate.status_code, 400)
        for _ in range(2):
            self.assertEqual(self.manager.post("/api/wechat/manage/papers/", self.payload(doi=""), format="json").status_code, 201)

    def test_search_topic_filter_and_no_login_for_public_list(self):
        self.upload(is_visible=True, journal="Nature Sustainability", authors="Test Author")
        for term in ["堆肥", "composting", "10.1234/test", "sustainability", "Test Author"]:
            result = self.public.get("/api/wechat/papers/", {"search": term})
            self.assertEqual(result.status_code, 200)
            self.assertEqual(result.data["count"], 1)
        self.assertEqual(self.public.get("/api/wechat/papers/", {"topic": "soil"}).data["count"], 0)

    def test_anonymous_and_ordinary_member_cannot_manage(self):
        self.assertIn(self.public.get("/api/wechat/manage/papers/").status_code, [401, 403])
        self.assertIn(self.public.post("/api/wechat/manage/papers/", self.payload()).status_code, [401, 403])
        user = get_user_model().objects.create_user("reader", password="test")
        user.profile.is_approved = True
        user.profile.save()
        self.public.force_authenticate(user)
        self.assertEqual(self.public.post("/api/wechat/manage/papers/", self.payload()).status_code, 403)

    def test_metadata_patch_preserves_pdf_and_remove_unlinks_it(self):
        pk = self.upload().data["id"]
        name = OriginalPaper.objects.get(pk=pk).pdf.name
        self.manager.patch(f"/api/wechat/manage/papers/{pk}/", {"journal": "Nature"}, format="json")
        self.assertEqual(OriginalPaper.objects.get(pk=pk).pdf.name, name)
        response = self.manager.patch(f"/api/wechat/manage/papers/{pk}/", {"remove_pdf": True}, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.data["has_pdf"])

    def test_missing_file_returns_404(self):
        paper = OriginalPaper.objects.create(**self.payload(), is_visible=True, pdf="original_papers/missing.pdf", sharing="authorized", rights_note="Permission")
        self.assertEqual(self.public.get(f"/api/wechat/papers/{paper.pk}/download/").status_code, 404)

    def test_fake_wechat_link_rejected(self):
        result = self.upload(wechat_url="https://example.com/not-wechat")
        self.assertEqual(result.status_code, 400)

    def test_editor_can_save_browser_multipart_payload_with_empty_year(self):
        user = get_user_model().objects.create_user("paper-editor", password="test")
        user.profile.is_approved = True
        user.profile.save()
        UserRole.objects.create(user=user, role=Role.objects.get(code=RoleCode.EDITOR))
        self.manager.force_authenticate(user)
        result = self.upload(year="", remove_pdf="false", is_visible="false")
        self.assertEqual(result.status_code, 201, result.data)
        self.assertIsNone(result.data["year"])
        self.assertFalse(result.data["is_visible"])

    @patch("apps.wechat_articles.paper_serializers.fetch_paper_metadata")
    def test_only_doi_and_pdf_are_enough_to_create(self, lookup):
        lookup.return_value = {"title": "Automatic paper title", "authors": "A. Author", "journal": "Nature",
                               "year": 2026, "publisher_url": "https://doi.org/10.1234/test", "topic": "compost"}
        result = self.manager.post("/api/wechat/manage/papers/", {
            "doi": "https://doi.org/10.1234/TEST",
            "title": "", "authors": "", "journal": "", "year": "", "topic": "", "publisher_url": "",
            "pdf": SimpleUploadedFile("paper.pdf", b"%PDF-1.4\n%%EOF", "application/pdf"),
        }, format="multipart")
        self.assertEqual(result.status_code, 201, result.data)
        self.assertEqual(result.data["title"], "Automatic paper title")
        self.assertEqual(result.data["journal"], "Nature")
        self.assertEqual(result.data["year"], 2026)
        self.assertEqual(result.data["topic"], "compost")
        self.assertTrue(result.data["has_pdf"])
        self.assertFalse(result.data["is_visible"])
        self.assertEqual(result.data["sharing"], "link_only")
        lookup.assert_called_once_with("10.1234/test")

    @patch("apps.wechat_articles.paper_serializers.fetch_paper_metadata")
    def test_lookup_failure_does_not_save_partial_record(self, lookup):
        lookup.side_effect = MetadataError("暂时无法连接 Crossref")
        result = self.manager.post("/api/wechat/manage/papers/", {"doi": "10.1234/test", "title": "", "topic": ""}, format="json")
        self.assertEqual(result.status_code, 400)
        self.assertIn("doi", result.data)
        self.assertEqual(OriginalPaper.objects.count(), 0)

    @patch("apps.wechat_articles.paper_serializers.fetch_paper_metadata")
    def test_manual_title_does_not_require_network_or_topic(self, lookup):
        result = self.manager.post("/api/wechat/manage/papers/", {"title": "Manually entered paper"}, format="json")
        self.assertEqual(result.status_code, 201, result.data)
        self.assertEqual(result.data["topic_label"], "未分类")
        lookup.assert_not_called()

    @patch("apps.wechat_articles.paper_views.fetch_paper_metadata")
    def test_metadata_lookup_requires_management_permission_and_does_not_save(self, lookup):
        lookup.return_value = {"doi": "10.1234/test", "title": "Paper", "metadata_source": "Crossref"}
        self.assertIn(self.public.post("/api/wechat/manage/papers/lookup/", {"doi": "10.1234/test"}).status_code, [401, 403])
        lookup.assert_not_called()
        result = self.manager.post("/api/wechat/manage/papers/lookup/", {"doi": "10.1234/test"}, format="json")
        self.assertEqual(result.status_code, 200)
        self.assertEqual(result.data["metadata_source"], "Crossref")
        self.assertEqual(OriginalPaper.objects.count(), 0)

    @override_settings(PROTECTED_MEDIA_ACCEL_PREFIX="/protected-media")
    def test_production_file_uses_internal_nginx_redirect(self):
        response = self.upload(is_visible=True, sharing="authorized", rights_note="Permission")
        result = self.public.get(f'/api/wechat/papers/{response.data["id"]}/download/')
        self.assertEqual(result.status_code, 200)
        self.assertTrue(result["X-Accel-Redirect"].startswith("/protected-media/original_papers/"))
