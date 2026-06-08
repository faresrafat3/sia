"""
GENESIS Web Search Tool
========================
Stolen from:
  - DeepResearcher (arXiv:2504.03160) — tool call format + short-term memory
  - A-RAG (arXiv:2602.03442) — 3-level search modes (quick/deep/read)
  - SAGE (arXiv:2602.05975) — keyword extraction before query (BM25 insight)
  - WebThinker (NeurIPS 2025) — evidence tracking per claim

Usage inside target_agent.py:
    from genesis.tools.web_search import web_search, extract_keywords, EvidenceLog

    results = web_search("Clickworker payment proof Egypt", mode="quick")
    full_page = web_search("https://reddit.com/r/...", mode="read")
    keywords = extract_keywords("مهام مدفوعة للمصريين", llm_client)
"""

from __future__ import annotations

import json
import logging
import os
import time
from dataclasses import dataclass, field, asdict
from typing import Any
from datetime import datetime

import httpx

logger = logging.getLogger(__name__)

# ─── Config ────────────────────────────────────────────────────────────────────
SERPER_URL = "https://google.serper.dev/search"
JINA_BASE = "https://r.jina.ai/"
DEFAULT_TIMEOUT = 30
JINA_TIMEOUT = 60
MAX_PAGE_CHARS = 6000   # max chars from full page read
MAX_SNIPPET_CHARS = 400


# ─── Result Types ──────────────────────────────────────────────────────────────
@dataclass
class SearchResult:
    """Single search result — always has source tracking (stolen from Rulers)."""
    title: str
    url: str
    snippet: str
    date: str = "unknown"
    mode: str = "quick"
    credibility_hint: str = "search_result"  # search_result | full_page | news
    content: str = ""  # only for mode="deep"/"read"

    def to_dict(self) -> dict:
        return asdict(self)

    def cite(self) -> str:
        """Short citation string for embedding in report."""
        date_str = f" ({self.date})" if self.date != "unknown" else ""
        return f"[{self.title[:50]}]{date_str} — {self.url}"


@dataclass
class EvidenceClaim:
    """
    Stolen from Rulers (arXiv:2601.08654) — schema-constrained evidence anchoring.
    Each claim MUST be tied to a source. Unanchored claims = hallucination.
    """
    claim: str
    source_url: str | None
    source_title: str | None
    source_date: str
    confidence: str  # HIGH | MEDIUM | LOW | UNVERIFIED
    quote: str = ""  # exact quote from source supporting the claim

    @property
    def is_verified(self) -> bool:
        return self.confidence in ("HIGH", "MEDIUM") and self.source_url is not None

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class EvidenceLog:
    """
    Short-term memory for evidence (stolen from DeepResearcher).
    Tracks all claims made during research with their sources.
    Saved as evidence_log.json — used by LLM-as-Judge for hallucination scoring.
    """
    claims: list[EvidenceClaim] = field(default_factory=list)
    searches_performed: int = 0
    pages_read: int = 0
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def add_claim(
        self,
        claim: str,
        source_url: str | None = None,
        source_title: str | None = None,
        source_date: str = "unknown",
        confidence: str = "UNVERIFIED",
        quote: str = "",
    ) -> EvidenceClaim:
        ec = EvidenceClaim(
            claim=claim,
            source_url=source_url,
            source_title=source_title,
            source_date=source_date,
            confidence=confidence,
            quote=quote,
        )
        self.claims.append(ec)
        return ec

    @property
    def hallucination_rate(self) -> float:
        """Fraction of unverified claims — signal for Regime Detector."""
        if not self.claims:
            return 0.0
        unverified = sum(1 for c in self.claims if not c.is_verified)
        return unverified / len(self.claims)

    @property
    def verified_count(self) -> int:
        return sum(1 for c in self.claims if c.is_verified)

    def save(self, path: str) -> None:
        data = {
            "summary": {
                "total_claims": len(self.claims),
                "verified_claims": self.verified_count,
                "hallucination_rate": self.hallucination_rate,
                "searches_performed": self.searches_performed,
                "pages_read": self.pages_read,
                "created_at": self.created_at,
            },
            "claims": [c.to_dict() for c in self.claims],
        }
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        logger.info(f"Evidence log saved: {path} ({len(self.claims)} claims, {self.hallucination_rate:.0%} unverified)")

    @classmethod
    def load(cls, path: str) -> "EvidenceLog":
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        log = cls()
        log.searches_performed = data["summary"].get("searches_performed", 0)
        log.pages_read = data["summary"].get("pages_read", 0)
        log.created_at = data["summary"].get("created_at", "unknown")
        for c in data.get("claims", []):
            log.claims.append(EvidenceClaim(**c))
        return log


# ─── Core Search Functions ─────────────────────────────────────────────────────

def web_search(
    query: str,
    mode: str = "quick",
    num_results: int = 10,
    serper_key: str | None = None,
    evidence_log: EvidenceLog | None = None,
    retry: int = 2,
) -> list[SearchResult]:
    """
    Main search function — stolen from DeepResearcher + A-RAG.

    Modes:
      "quick" — snippet only via Serper (fast, cheap, ~0.001$/search)
      "deep"  — snippet + first paragraphs of top result via Jina
      "read"  — full page content of a specific URL via Jina

    Args:
        query: search query OR URL (for mode="read")
        mode: "quick" | "deep" | "read"
        num_results: max results for quick/deep
        serper_key: API key (falls back to env SERPER_API_KEY)
        evidence_log: if provided, increments search counters
        retry: retry count on network failure

    Returns:
        list[SearchResult] — always returns list (empty on failure)
    """
    key = serper_key or os.getenv("SERPER_API_KEY") or os.getenv("WEB_SEARCH_API_KEY")

    if mode == "read":
        return _jina_read(query, evidence_log=evidence_log)

    # quick or deep — Serper first
    results = _serper_search(query, num_results=num_results, key=key,
                             retry=retry, evidence_log=evidence_log)

    if mode == "deep" and results:
        # Enrich top result with full content
        top = results[0]
        page_data = _jina_read(top.url, evidence_log=None)
        if page_data:
            top.content = page_data[0].content
            top.mode = "deep"

    return results


def _serper_search(
    query: str,
    num_results: int,
    key: str | None,
    retry: int,
    evidence_log: EvidenceLog | None,
) -> list[SearchResult]:
    """Serper Google Search API."""
    if not key:
        logger.warning("No SERPER_API_KEY — web_search returning empty. Set env var.")
        return []

    for attempt in range(retry + 1):
        try:
            resp = httpx.post(
                SERPER_URL,
                headers={"X-API-KEY": key, "Content-Type": "application/json"},
                json={"q": query, "num": num_results},
                timeout=DEFAULT_TIMEOUT,
            )
            resp.raise_for_status()
            data = resp.json()

            results: list[SearchResult] = []

            # Organic results
            for r in data.get("organic", []):
                results.append(SearchResult(
                    title=r.get("title", "")[:120],
                    url=r.get("link", ""),
                    snippet=(r.get("snippet", ""))[:MAX_SNIPPET_CHARS],
                    date=r.get("date", "unknown"),
                    mode="quick",
                    credibility_hint="organic",
                ))

            # News results (often have dates)
            for r in data.get("news", []):
                results.append(SearchResult(
                    title=r.get("title", "")[:120],
                    url=r.get("link", ""),
                    snippet=(r.get("snippet", ""))[:MAX_SNIPPET_CHARS],
                    date=r.get("date", "unknown"),
                    mode="quick",
                    credibility_hint="news",
                ))

            if evidence_log is not None:
                evidence_log.searches_performed += 1

            logger.info(f"Serper search: '{query[:60]}' → {len(results)} results")
            return results

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 429:
                logger.warning(f"Serper rate limit — attempt {attempt+1}/{retry+1}")
                time.sleep(2 ** attempt)
            else:
                logger.error(f"Serper HTTP error {e.response.status_code}: {e}")
                break
        except Exception as e:
            logger.error(f"Serper search failed (attempt {attempt+1}): {e}")
            if attempt < retry:
                time.sleep(1)

    return []


def _jina_read(
    url: str,
    evidence_log: EvidenceLog | None = None,
) -> list[SearchResult]:
    """
    Jina AI Reader — reads full page content.
    Stolen from SimpleDeepSearcher (search-fetch-summarise loop).
    Free tier: unlimited reads (Jina's r.jina.ai).
    """
    try:
        jina_url = f"{JINA_BASE}{url}" if not url.startswith(JINA_BASE) else url
        resp = httpx.get(jina_url, timeout=JINA_TIMEOUT,
                         headers={"Accept": "text/plain"})
        resp.raise_for_status()
        content = resp.text[:MAX_PAGE_CHARS]

        if evidence_log is not None:
            evidence_log.pages_read += 1

        logger.info(f"Jina read: {url[:70]} → {len(content)} chars")
        return [SearchResult(
            title=f"Full page: {url[:60]}",
            url=url,
            snippet=content[:MAX_SNIPPET_CHARS],
            date=datetime.now().strftime("%Y-%m-%d"),
            mode="read",
            credibility_hint="full_page",
            content=content,
        )]
    except Exception as e:
        logger.error(f"Jina read failed for {url}: {e}")
        return []


# ─── Keyword Extractor (SAGE insight) ──────────────────────────────────────────

def extract_keywords(
    query: str,
    llm_client: Any | None = None,
    fallback_split: bool = True,
) -> list[str]:
    """
    Stolen from SAGE (arXiv:2602.05975):
    BM25 > LLM retrievers when agents use precise keywords instead of long queries.
    
    Extracts 3-5 precise keywords from a natural language query.
    Use these for additional targeted searches alongside the full query.

    Args:
        query: natural language query (Arabic or English)
        llm_client: openai.OpenAI client (optional — falls back to split)
        fallback_split: if no LLM, use simple word split
    
    Returns:
        list of keywords (3-5)
    """
    if llm_client is not None:
        try:
            resp = llm_client.chat.completions.create(
                model=os.getenv("TASK_MODEL", "openai/gpt-oss-20b:free"),
                messages=[{
                    "role": "user",
                    "content": (
                        f"Extract 3-5 precise search keywords from this query. "
                        f"Keywords should be specific nouns/terms, not generic words.\n\n"
                        f"Query: {query}\n\n"
                        f"Return JSON only: {{\"keywords\": [\"kw1\", \"kw2\", \"kw3\"]}}"
                    ),
                }],
                max_tokens=80,
                temperature=0.0,
            )
            content = resp.choices[0].message.content or ""
            # parse JSON
            start = content.find("{")
            end = content.rfind("}") + 1
            if start >= 0 and end > start:
                data = json.loads(content[start:end])
                kws = data.get("keywords", [])
                if kws:
                    logger.info(f"Keywords extracted: {kws}")
                    return kws[:5]
        except Exception as e:
            logger.warning(f"Keyword extraction via LLM failed: {e}")

    if fallback_split:
        # Simple fallback: take significant words (len > 3, skip stopwords)
        stopwords = {"the", "and", "for", "with", "from", "that", "this",
                     "في", "من", "على", "إلى", "مع", "هل", "كيف", "ما"}
        words = [w.strip(".,?!؟") for w in query.split()]
        keywords = [w for w in words if len(w) > 3 and w.lower() not in stopwords]
        return keywords[:5]

    return []


# ─── Multi-Query Search (DeepResearcher pattern) ───────────────────────────────

def multi_query_search(
    queries: list[str],
    mode: str = "quick",
    num_results: int = 5,
    serper_key: str | None = None,
    evidence_log: EvidenceLog | None = None,
    deduplicate: bool = True,
) -> list[SearchResult]:
    """
    Search with multiple queries simultaneously (stolen from DeepResearcher).
    DeepResearcher sends multiple queries in one tool call for efficiency.
    
    Args:
        queries: list of queries to search
        deduplicate: remove duplicate URLs across queries
    
    Returns:
        combined list of SearchResult, sorted by source diversity
    """
    all_results: list[SearchResult] = []
    seen_urls: set[str] = set()

    for q in queries:
        results = web_search(
            q, mode=mode, num_results=num_results,
            serper_key=serper_key, evidence_log=evidence_log
        )
        for r in results:
            if deduplicate and r.url in seen_urls:
                continue
            seen_urls.add(r.url)
            all_results.append(r)

        # Rate limit protection
        if len(queries) > 2:
            time.sleep(0.3)

    logger.info(f"Multi-query search: {len(queries)} queries → {len(all_results)} unique results")
    return all_results


# ─── Format helpers ────────────────────────────────────────────────────────────

def format_results_for_prompt(results: list[SearchResult], max_results: int = 5) -> str:
    """
    Format search results for embedding in LLM prompt.
    Used inside target_agent.py to inject evidence into reasoning.
    """
    if not results:
        return "لا توجد نتائج بحث."

    lines = [f"نتائج البحث ({min(len(results), max_results)} من {len(results)}):"]
    for i, r in enumerate(results[:max_results], 1):
        lines.append(f"\n[{i}] {r.title}")
        lines.append(f"    URL: {r.url}")
        if r.date != "unknown":
            lines.append(f"    التاريخ: {r.date}")
        lines.append(f"    المقتطف: {r.snippet}")
        if r.content:
            lines.append(f"    المحتوى الكامل (أول 500 حرف): {r.content[:500]}")

    return "\n".join(lines)


def results_to_dict(results: list[SearchResult]) -> list[dict]:
    """Serialize results for saving to JSON."""
    return [r.to_dict() for r in results]
