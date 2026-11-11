import json
from unittest.mock import MagicMock, patch
from urllib.error import HTTPError, URLError

from django.core.cache import cache
from django.test import SimpleTestCase

from .paper_metadata import MetadataError, fetch_paper_metadata, infer_topic, normalize_doi


class PaperMetadataTests(SimpleTestCase):
    def setUp(self):
        cache.clear()

    def response(self, message):
        response = MagicMock()
        response.__enter__.return_value.read.return_value = json.dumps({"message": message}).encode()
        return response

    @patch("apps.wechat_articles.paper_metadata.urlopen")
    def test_crossref_mapping_normalization_date_and_cache(self, urlopen):
        urlopen.return_value = self.response({
            "DOI": "10.1234/Test", "title": ["Composting <i>organic</i> residues &amp; nutrients"],
            "container-title": ["Test Journal"], "author": [{"given": "First", "family": "Author"}, {"name": "Study Group"}],
            "published-online": {"date-parts": [[2025, 12, 1]]}, "published-print": {"date-parts": [[2026]]},
            "license": [{"URL": "https://creativecommons.org/licenses/by/4.0/"}],
        })
        result = fetch_paper_metadata("https://doi.org/10.1234/TEST")
        self.assertEqual(result["title"], "Composting organic residues & nutrients")
        self.assertEqual(result["authors"], "First Author; Study Group")
        self.assertEqual(result["year"], 2025)
        self.assertEqual(result["topic"], "compost")
        self.assertNotIn("sharing", result)
        self.assertNotIn("rights_note", result)
        self.assertNotIn("is_visible", result)
        self.assertEqual(fetch_paper_metadata("10.1234/test"), result)
        urlopen.assert_called_once()
        self.assertEqual(urlopen.call_args.args[0].full_url, "https://api.crossref.org/works/10.1234%2Ftest")

    @patch("apps.wechat_articles.paper_metadata.urlopen")
    def test_identity_mismatch_is_rejected(self, urlopen):
        urlopen.return_value = self.response({"DOI": "10.1234/other", "title": ["Wrong paper"]})
        with self.assertRaisesRegex(MetadataError, "不一致"):
            fetch_paper_metadata("10.1234/test")

    @patch("apps.wechat_articles.paper_metadata.urlopen")
    def test_missing_title_is_not_replaced_with_a_fake_title(self, urlopen):
        urlopen.return_value = self.response({"DOI": "10.1234/test"})
        with self.assertRaises(MetadataError):
            fetch_paper_metadata("10.1234/test")

    @patch("apps.wechat_articles.paper_metadata.urlopen")
    def test_http_and_network_failures_are_actionable(self, urlopen):
        for exc in [HTTPError("https://api.crossref.org", 404, "not found", {}, None), URLError("timeout")]:
            urlopen.side_effect = exc
            with self.assertRaises(MetadataError):
                fetch_paper_metadata("10.1234/test")

    @patch("apps.wechat_articles.paper_metadata.urlopen")
    def test_invalid_doi_never_triggers_a_request(self, urlopen):
        for value in ["", "https://localhost/", "10.1234/test space"]:
            with self.assertRaises(MetadataError):
                fetch_paper_metadata(value)
        urlopen.assert_not_called()

    def test_topic_classification_has_no_arbitrary_default(self):
        self.assertEqual(infer_topic("Unrelated research", []), "")
        self.assertEqual(infer_topic("Phosphorus recovery from manure", []), "nutrients")
        self.assertEqual(normalize_doi("DOI: 10.1234/TEST"), "10.1234/test")
