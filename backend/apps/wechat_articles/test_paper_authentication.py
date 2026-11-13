import hashlib
from tempfile import TemporaryDirectory
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.files.storage import FileSystemStorage
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from rest_framework.test import APIClient

from .models import OriginalPaper

TOKEN = "test-only-original-paper-token-not-a-live-secret-12345"


@override_settings(LABHUB_PAPER_UPLOAD_TOKEN_SHA256=hashlib.sha256(TOKEN.encode()).hexdigest())
class PaperUploadAuthenticationTests(TestCase):
    def setUp(self):
        self.directory = TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        field = OriginalPaper._meta.get_field("pdf")
        old_storage = field.storage
        field.storage = FileSystemStorage(location=self.directory.name)
        self.addCleanup(setattr, field, "storage", old_storage)
        self.client = APIClient(enforce_csrf_checks=True)
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + TOKEN)

    def upload(self, **extra):
        return self.client.post("/api/wechat/manage/papers/", {
            "doi": "10.1234/token-test", "title": "Verified English title",
            "pdf": SimpleUploadedFile("paper.pdf", b"%PDF-1.4\n%%EOF", "application/pdf"),
            **extra,
        }, format="multipart")

    def test_token_upload_and_readback_without_session_or_csrf(self):
        r = self.upload()
        self.assertEqual(r.status_code, 201, r.data)
        self.assertTrue(r.data["has_pdf"])
        self.assertFalse(r.data["is_visible"])
        self.assertEqual(self.client.get("/api/wechat/manage/papers/").status_code, 200)
        self.assertEqual(self.client.get(f'/api/wechat/manage/papers/{r.data["id"]}/').status_code, 200)
        self.assertNotIn("sessionid", self.client.cookies)

    @patch("apps.wechat_articles.paper_serializers.fetch_paper_metadata")
    def test_only_doi_and_pdf_uses_existing_metadata_lookup(self, lookup):
        lookup.return_value = {"title": "English title from Crossref", "authors": "A. Author",
            "journal": "Journal", "year": 2026, "publisher_url": "https://doi.org/10.1234/token-test", "topic": "environment"}
        r = self.upload(title="")
        self.assertEqual(r.status_code, 201, r.data)
        self.assertEqual(r.data["title"], "English title from Crossref")
        self.assertEqual(r.data["topic"], "environment")
        lookup.assert_called_once_with("10.1234/token-test")

    def test_explicit_sharing_can_be_public(self):
        r = self.upload(is_visible=True, sharing="authorized", rights_note="User authorization recorded separately")
        self.assertEqual(r.status_code, 201, r.data)
        public = APIClient().get(r.data["download_url"])
        self.assertEqual(public.status_code, 200)
        self.assertEqual(b"".join(public.streaming_content), b"%PDF-1.4\n%%EOF")
        public.close()

    def test_missing_or_invalid_token_cannot_create(self):
        for value in [None, "Bearer incorrect-token-of-sufficient-length", "Bearer", "Bearer a b"]:
            self.client.credentials(**({"HTTP_AUTHORIZATION": value} if value else {}))
            self.assertEqual(self.upload().status_code, 401)
        self.assertEqual(OriginalPaper.objects.count(), 0)

    @override_settings(LABHUB_PAPER_UPLOAD_TOKEN_SHA256="")
    def test_default_disabled(self):
        self.assertEqual(self.upload().status_code, 401)

    @override_settings(LABHUB_PAPER_UPLOAD_TOKEN_SHA256="bad-setting")
    def test_malformed_server_hash_is_disabled(self):
        self.assertEqual(self.upload().status_code, 401)

    @override_settings(LABHUB_PAPER_UPLOAD_TOKEN_SHA256="非" * 64)
    def test_non_ascii_server_hash_is_rejected_not_a_server_error(self):
        self.assertEqual(self.upload().status_code, 401)

    def test_token_cannot_update_delete_or_unlink_existing_files(self):
        r = self.upload()
        url = f'/api/wechat/manage/papers/{r.data["id"]}/'
        self.assertEqual(self.client.patch(url, {"remove_pdf": True}, format="json").status_code, 403)
        self.assertEqual(self.client.put(url, {"title": "Changed"}, format="json").status_code, 403)
        self.assertEqual(self.client.delete(url).status_code, 403)
        self.assertTrue(OriginalPaper.objects.get(pk=r.data["id"]).pdf)

    def test_token_is_not_an_account_or_other_cms_credential(self):
        for url in ["/api/accounts/auth/me/", "/api/wechat/manage/accounts/"]:
            self.assertIn(self.client.get(url).status_code, [401, 403])

    def test_duplicate_doi_remains_rejected(self):
        self.assertEqual(self.upload().status_code, 201)
        self.assertEqual(self.upload().status_code, 400)
        self.assertEqual(OriginalPaper.objects.count(), 1)

    def test_existing_login_csrf_protection_is_preserved(self):
        user = get_user_model().objects.create_superuser("existing-manager", "manager@example.com", "test")
        self.client.credentials()
        self.client.force_login(user)
        self.assertEqual(self.upload().status_code, 403)

    def test_invalid_pdf_is_still_rejected(self):
        r = self.upload(pdf=SimpleUploadedFile("bad.pdf", b"not a PDF", "application/pdf"))
        self.assertEqual(r.status_code, 400)

    def test_sharing_still_requires_a_rights_note(self):
        self.assertEqual(self.upload(sharing="authorized").status_code, 400)
