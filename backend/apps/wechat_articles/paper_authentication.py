"""A separately revocable credential scoped to original-paper ingestion."""
import hashlib
import hmac
import re
from dataclasses import dataclass

from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from rest_framework.authentication import BaseAuthentication, get_authorization_header
from rest_framework.exceptions import AuthenticationFailed

from apps.accounts.permissions import CanManagePortalContent


@dataclass(frozen=True)
class PaperUploadCredential:
    scope: str = "original-paper-ingest"


class PaperUploadTokenAuthentication(BaseAuthentication):
    def authenticate(self, request):
        header = get_authorization_header(request).split()
        if not header or header[0].lower() != b"bearer":
            return None
        expected = settings.LABHUB_PAPER_UPLOAD_TOKEN_SHA256
        if len(header) != 2 or not 32 <= len(header[1]) <= 512 or not re.fullmatch(r"[a-f0-9]{64}", expected):
            raise AuthenticationFailed("论文上传凭证无效或未启用。")
        actual = hashlib.sha256(header[1]).hexdigest()
        if not hmac.compare_digest(actual, expected):
            raise AuthenticationFailed("论文上传凭证无效或未启用。")
        # This credential is deliberately not a user login or a staff account.
        return AnonymousUser(), PaperUploadCredential()

    def authenticate_header(self, request):
        return 'Bearer realm="original-paper-ingest"'


class CanIngestOriginalPapers(CanManagePortalContent):
    def has_permission(self, request, view):
        if isinstance(request.auth, PaperUploadCredential):
            return view.action in {"create", "list", "retrieve", "lookup"}
        return super().has_permission(request, view)
