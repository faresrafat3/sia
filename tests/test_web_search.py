"""
Tests for genesis/tools/web_search.py
Stolen methodology:
  - DeepResearcher (2504.03160) — tool format + evidence memory
  - A-RAG (2602.03442) — 3 search modes
  - SAGE (2602.05975) — keyword extraction
  - Rulers (2601.08654) — schema-constrained evidence
"""
import json
import os
import tempfile
import unittest
from unittest.mock import patch, MagicMock

from genesis.tools.web_search import (
    SearchResult,
    EvidenceClaim,
    EvidenceLog,
    extract_keywords,
    format_results_for_prompt,
    results_to_dict,
)


# ─── SearchResult Tests ────────────────────────────────────────────────────────
class TestSearchResult(unittest.TestCase):
    def _make(self, **kwargs):
        defaults = dict(title="Test Title", url="https://example.com",
                        snippet="Test snippet")
        defaults.update(kwargs)
        return SearchResult(**defaults)

    def test_basic_fields(self):
        r = self._make(date="2025-03-15", credibility_hint="organic")
        self.assertEqual(r.title, "Test Title")
        self.assertEqual(r.date, "2025-03-15")
        self.assertEqual(r.credibility_hint, "organic")

    def test_cite_with_date(self):
        r = self._make(date="2025-06-01")
        cite = r.cite()
        self.assertIn("2025-06-01", cite)
        self.assertIn("https://example.com", cite)

    def test_cite_without_date(self):
        r = self._make(date="unknown")
        cite = r.cite()
        self.assertNotIn("unknown", cite)
        self.assertIn("example.com", cite)

    def test_to_dict(self):
        r = self._make()
        d = r.to_dict()
        self.assertIsInstance(d, dict)
        self.assertIn("title", d)
        self.assertIn("url", d)
        self.assertIn("snippet", d)

    def test_default_mode(self):
        r = self._make()
        self.assertEqual(r.mode, "quick")

    def test_content_field(self):
        r = self._make(content="Full page text here")
        self.assertEqual(r.content, "Full page text here")


# ─── EvidenceClaim Tests ───────────────────────────────────────────────────────
class TestEvidenceClaim(unittest.TestCase):
    def test_verified_high(self):
        ec = EvidenceClaim(
            claim="test", source_url="https://example.com",
            source_title="Example", source_date="2025-01-01",
            confidence="HIGH", quote="exact quote"
        )
        self.assertTrue(ec.is_verified)

    def test_verified_medium(self):
        ec = EvidenceClaim(
            claim="test", source_url="https://example.com",
            source_title="Example", source_date="2025-01-01",
            confidence="MEDIUM", quote=""
        )
        self.assertTrue(ec.is_verified)

    def test_unverified_no_url(self):
        ec = EvidenceClaim(
            claim="test", source_url=None,
            source_title=None, source_date="unknown",
            confidence="HIGH", quote=""
        )
        self.assertFalse(ec.is_verified)  # no URL = not verified

    def test_unverified_confidence(self):
        ec = EvidenceClaim(
            claim="test", source_url="https://example.com",
            source_title="Example", source_date="2025-01-01",
            confidence="UNVERIFIED", quote=""
        )
        self.assertFalse(ec.is_verified)

    def test_low_confidence_not_verified(self):
        ec = EvidenceClaim(
            claim="test", source_url="https://example.com",
            source_title="Ex", source_date="2025-01-01",
            confidence="LOW", quote=""
        )
        self.assertFalse(ec.is_verified)

    def test_to_dict(self):
        ec = EvidenceClaim(
            claim="test claim", source_url="https://x.com",
            source_title="X", source_date="2025-06-08",
            confidence="HIGH", quote="text"
        )
        d = ec.to_dict()
        self.assertEqual(d["claim"], "test claim")
        self.assertEqual(d["confidence"], "HIGH")
        self.assertEqual(d["quote"], "text")


# ─── EvidenceLog Tests ────────────────────────────────────────────────────────
class TestEvidenceLog(unittest.TestCase):
    def test_empty_log(self):
        log = EvidenceLog()
        self.assertEqual(len(log.claims), 0)
        self.assertEqual(log.hallucination_rate, 0.0)
        self.assertEqual(log.verified_count, 0)

    def test_add_verified_claim(self):
        log = EvidenceLog()
        ec = log.add_claim(
            "Platform X works in Egypt",
            source_url="https://reddit.com/r/beermoney/test",
            source_title="Reddit proof",
            source_date="2025-03-15",
            confidence="HIGH",
            quote="Works fine from Egypt"
        )
        self.assertEqual(len(log.claims), 1)
        self.assertTrue(ec.is_verified)
        self.assertEqual(log.verified_count, 1)
        self.assertEqual(log.hallucination_rate, 0.0)

    def test_add_unverified_claim(self):
        log = EvidenceLog()
        log.add_claim("Platform Y pays $50/day", confidence="UNVERIFIED")
        self.assertEqual(log.hallucination_rate, 1.0)
        self.assertEqual(log.verified_count, 0)

    def test_mixed_claims_hallucination_rate(self):
        log = EvidenceLog()
        log.add_claim("Claim A", source_url="https://x.com", source_title="X",
                      source_date="2025-01-01", confidence="HIGH")
        log.add_claim("Claim B", confidence="UNVERIFIED")
        log.add_claim("Claim C", confidence="UNVERIFIED")
        # 2 out of 3 unverified
        self.assertAlmostEqual(log.hallucination_rate, 2/3, places=5)
        self.assertEqual(log.verified_count, 1)

    def test_save_and_load(self):
        log = EvidenceLog()
        log.searches_performed = 5
        log.pages_read = 2
        log.add_claim("Test claim", source_url="https://example.com",
                      source_title="Example", source_date="2025-06-08",
                      confidence="MEDIUM", quote="test quote")
        log.add_claim("Unverified", confidence="UNVERIFIED")

        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            path = f.name

        try:
            log.save(path)

            # Verify file structure
            with open(path) as f:
                data = json.load(f)
            self.assertIn("summary", data)
            self.assertIn("claims", data)
            self.assertEqual(data["summary"]["total_claims"], 2)
            self.assertEqual(data["summary"]["searches_performed"], 5)
            self.assertAlmostEqual(data["summary"]["hallucination_rate"], 0.5, places=5)

            # Load back
            loaded = EvidenceLog.load(path)
            self.assertEqual(len(loaded.claims), 2)
            self.assertEqual(loaded.searches_performed, 5)
            self.assertEqual(loaded.pages_read, 2)
            self.assertAlmostEqual(loaded.hallucination_rate, 0.5, places=5)
        finally:
            os.unlink(path)

    def test_counter_increment(self):
        log = EvidenceLog()
        log.searches_performed += 1
        log.pages_read += 1
        self.assertEqual(log.searches_performed, 1)
        self.assertEqual(log.pages_read, 1)


# ─── extract_keywords Tests ───────────────────────────────────────────────────
class TestExtractKeywords(unittest.TestCase):
    def test_no_llm_fallback(self):
        # Without LLM — simple split (fallback_split=True default)
        kws = extract_keywords("micro-task platforms available in Egypt without VPN")
        self.assertIsInstance(kws, list)
        self.assertGreater(len(kws), 0)
        self.assertLessEqual(len(kws), 5)

    def test_arabic_query_fallback(self):
        kws = extract_keywords("منصات مهام مدفوعة متاحة للمصريين بدون في بي إن")
        self.assertIsInstance(kws, list)
        self.assertGreater(len(kws), 0)

    def test_short_words_filtered(self):
        # Short words (<=3 chars) should be filtered in fallback
        kws = extract_keywords("find platforms Egypt pay 2025 data", llm_client=None)
        for kw in kws:
            self.assertGreater(len(kw), 3)

    def test_stopwords_filtered(self):
        kws = extract_keywords("the best and most reliable platforms", llm_client=None)
        for kw in kws:
            self.assertNotIn(kw.lower(), {"the", "and", "for", "with"})

    def test_with_mock_llm(self):
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices[0].message.content = '{"keywords": ["Appen", "Egypt", "payment"]}'
        mock_client.chat.completions.create.return_value = mock_response

        kws = extract_keywords("Appen payment proof Egypt 2025", llm_client=mock_client)
        self.assertEqual(kws, ["Appen", "Egypt", "payment"])

    def test_with_mock_llm_bad_json(self):
        # Fallback to split if LLM returns bad JSON
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices[0].message.content = "not valid json"
        mock_client.chat.completions.create.return_value = mock_response

        kws = extract_keywords("find micro task platforms Egypt", llm_client=mock_client)
        self.assertIsInstance(kws, list)  # falls back to split

    def test_max_5_keywords(self):
        kws = extract_keywords(
            "find reliable verified paid micro task platforms available in Egypt 2025 online"
        )
        self.assertLessEqual(len(kws), 5)

    def test_empty_query(self):
        kws = extract_keywords("")
        self.assertIsInstance(kws, list)


# ─── format_results_for_prompt Tests ─────────────────────────────────────────
class TestFormatResultsForPrompt(unittest.TestCase):
    def _make_results(self, n=3):
        return [
            SearchResult(
                title=f"Result {i}",
                url=f"https://example.com/{i}",
                snippet=f"Snippet for result {i}",
                date=f"2025-0{i+1}-01",
            )
            for i in range(n)
        ]

    def test_empty_results(self):
        text = format_results_for_prompt([])
        self.assertIn("لا توجد نتائج", text)

    def test_basic_format(self):
        results = self._make_results(3)
        text = format_results_for_prompt(results, max_results=3)
        self.assertIn("Result 0", text)
        self.assertIn("https://example.com/0", text)
        self.assertIn("Snippet for result 0", text)

    def test_max_results_respected(self):
        results = self._make_results(10)
        text = format_results_for_prompt(results, max_results=3)
        # Should only show 3 results
        self.assertIn("Result 0", text)
        self.assertIn("Result 1", text)
        self.assertIn("Result 2", text)
        self.assertNotIn("Result 9", text)

    def test_date_included(self):
        results = [SearchResult(
            title="Test", url="https://x.com",
            snippet="test", date="2025-06-08"
        )]
        text = format_results_for_prompt(results)
        self.assertIn("2025-06-08", text)

    def test_content_included_when_present(self):
        results = [SearchResult(
            title="Test", url="https://x.com",
            snippet="test", content="Full page content here"
        )]
        text = format_results_for_prompt(results)
        self.assertIn("Full page content", text)

    def test_arabic_output(self):
        results = self._make_results(1)
        text = format_results_for_prompt(results)
        self.assertIn("نتائج البحث", text)


# ─── results_to_dict Tests ───────────────────────────────────────────────────
class TestResultsToDict(unittest.TestCase):
    def test_basic(self):
        results = [
            SearchResult(title="T1", url="https://a.com", snippet="S1"),
            SearchResult(title="T2", url="https://b.com", snippet="S2"),
        ]
        dicts = results_to_dict(results)
        self.assertEqual(len(dicts), 2)
        self.assertEqual(dicts[0]["title"], "T1")
        self.assertEqual(dicts[1]["url"], "https://b.com")
        self.assertIsInstance(dicts[0], dict)

    def test_empty(self):
        dicts = results_to_dict([])
        self.assertEqual(dicts, [])


# ─── Integration: web_search mock tests ───────────────────────────────────────
class TestWebSearchMocked(unittest.TestCase):
    """Test web_search() with mocked HTTP — no real API calls."""

    def _mock_serper_response(self, n=3):
        return {
            "organic": [
                {
                    "title": f"Result {i}",
                    "link": f"https://example.com/{i}",
                    "snippet": f"Snippet {i}",
                    "date": f"2025-0{i+1}-01",
                }
                for i in range(n)
            ],
            "news": []
        }

    @patch("genesis.tools.web_search.httpx.post")
    def test_quick_search_returns_results(self, mock_post):
        from genesis.tools.web_search import web_search
        mock_resp = MagicMock()
        mock_resp.json.return_value = self._mock_serper_response(3)
        mock_resp.raise_for_status = MagicMock()
        mock_post.return_value = mock_resp

        os.environ["SERPER_API_KEY"] = "test_key"
        results = web_search("test query", mode="quick", num_results=3)

        self.assertEqual(len(results), 3)
        self.assertEqual(results[0].title, "Result 0")
        self.assertEqual(results[0].mode, "quick")
        self.assertEqual(results[1].date, "2025-02-01")

    @patch("genesis.tools.web_search.httpx.post")
    def test_evidence_log_incremented(self, mock_post):
        from genesis.tools.web_search import web_search
        mock_resp = MagicMock()
        mock_resp.json.return_value = self._mock_serper_response(2)
        mock_resp.raise_for_status = MagicMock()
        mock_post.return_value = mock_resp

        os.environ["SERPER_API_KEY"] = "test_key"
        log = EvidenceLog()
        web_search("test", mode="quick", evidence_log=log)
        self.assertEqual(log.searches_performed, 1)

    @patch("genesis.tools.web_search.httpx.post")
    def test_no_api_key_returns_empty(self, mock_post):
        from genesis.tools.web_search import web_search
        old_key = os.environ.pop("SERPER_API_KEY", None)
        try:
            results = web_search("test", mode="quick", serper_key=None)
            self.assertEqual(results, [])
        finally:
            if old_key:
                os.environ["SERPER_API_KEY"] = old_key

    @patch("genesis.tools.web_search.httpx.get")
    def test_jina_read_mode(self, mock_get):
        from genesis.tools.web_search import web_search
        mock_resp = MagicMock()
        mock_resp.text = "Full page content " * 100
        mock_resp.raise_for_status = MagicMock()
        mock_get.return_value = mock_resp

        results = web_search("https://example.com/page", mode="read")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].mode, "read")
        self.assertEqual(results[0].credibility_hint, "full_page")
        self.assertGreater(len(results[0].content), 0)

    @patch("genesis.tools.web_search.httpx.post")
    def test_news_results_included(self, mock_post):
        from genesis.tools.web_search import web_search
        mock_resp = MagicMock()
        mock_resp.json.return_value = {
            "organic": [{"title": "Organic", "link": "https://a.com", "snippet": "S"}],
            "news": [{"title": "News Item", "link": "https://b.com", "snippet": "N", "date": "Jun 2025"}]
        }
        mock_resp.raise_for_status = MagicMock()
        mock_post.return_value = mock_resp

        os.environ["SERPER_API_KEY"] = "test_key"
        results = web_search("test", mode="quick")
        self.assertEqual(len(results), 2)
        hints = {r.credibility_hint for r in results}
        self.assertIn("organic", hints)
        self.assertIn("news", hints)


if __name__ == "__main__":
    unittest.main(verbosity=2)
