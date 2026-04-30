"""
Endpoint accessibility test for brainimagelibrary.

Tests all HTTP endpoints used by the library, reporting whether each
is reachable and returns a non-empty response.

Usage:
    python test_endpoints.py
"""

import sys
import time
import requests

# ── constants ──────────────────────────────────────────────────────────────────
BIL_API   = "https://api.brainimagelibrary.org"
DOWNLOAD  = "https://download.brainimagelibrary.org"
DATACITE  = "https://api.datacite.org"
OPENCITE  = "https://opencitations.net"
CROSSREF  = "https://api.crossref.org"
SEMSCHOLAR = "https://api.semanticscholar.org"

BILDID    = "act-bag"
DOI_PREFIX = "10.35077"
DOI        = f"{DOI_PREFIX}/{BILDID}"
DIRECTORY  = "/bil/data/2019/02/13/H19.28.012.MITU.01.05"

TIMEOUT = 30  # seconds per request

# ── helpers ────────────────────────────────────────────────────────────────────

def _check(label: str, url: str, method: str = "GET") -> dict:
    """Hit *url* and return a result dict."""
    try:
        start = time.monotonic()
        if method == "HEAD":
            resp = requests.head(url, timeout=TIMEOUT)
        else:
            resp = requests.get(url, timeout=TIMEOUT)
        elapsed = time.monotonic() - start

        ok = resp.status_code == 200
        has_body = False
        body_preview = ""
        if method != "HEAD" and ok:
            try:
                data = resp.json()
                has_body = bool(data)
                if isinstance(data, dict):
                    body_preview = str(list(data.keys()))[:80]
                elif isinstance(data, list):
                    body_preview = f"[list, {len(data)} items]"
                else:
                    body_preview = str(data)[:80]
            except Exception:
                has_body = len(resp.content) > 0
                body_preview = f"<non-JSON, {len(resp.content)} bytes>"

        return {
            "label": label,
            "url": url,
            "status": resp.status_code,
            "ok": ok,
            "has_body": has_body,
            "elapsed": elapsed,
            "body_preview": body_preview,
        }
    except requests.exceptions.ConnectionError as exc:
        return {"label": label, "url": url, "status": None, "ok": False,
                "has_body": False, "elapsed": None, "body_preview": f"ConnectionError: {exc}"}
    except requests.exceptions.Timeout:
        return {"label": label, "url": url, "status": None, "ok": False,
                "has_body": False, "elapsed": None, "body_preview": "Timeout"}
    except Exception as exc:
        return {"label": label, "url": url, "status": None, "ok": False,
                "has_body": False, "elapsed": None, "body_preview": str(exc)}


def _truncate(s: str, n: int) -> str:
    return s if len(s) <= n else s[: n - 1] + "\u2026"


def _print_table(results: list) -> None:
    """Render results as a fixed-width table with ANSI colour."""
    # ANSI codes
    GREEN  = "\033[32m"
    YELLOW = "\033[33m"
    RED    = "\033[31m"
    BOLD   = "\033[1m"
    RESET  = "\033[0m"

    col_w = {"#": 3, "result": 6, "status": 6, "time": 7, "endpoint": 42, "response": 32}
    sep = "-+-".join("-" * w for w in col_w.values())

    def _row(*cells):
        widths = list(col_w.values())
        parts = []
        for cell, w in zip(cells, widths):
            parts.append(str(cell).ljust(w)[:w])
        return " | ".join(parts)

    header = _row("#", "Result", "Status", "Time(s)", "Endpoint", "Response keys/info")
    print()
    print(BOLD + header + RESET)
    print(sep)

    for i, r in enumerate(results, 1):
        mark = "PASS" if (r["ok"] and r["has_body"]) else ("WARN" if r["ok"] else "FAIL")
        colour = GREEN if mark == "PASS" else (YELLOW if mark == "WARN" else RED)

        status_str  = str(r["status"]) if r["status"] is not None else "N/A"
        elapsed_str = f"{r['elapsed']:.2f}" if r["elapsed"] is not None else "N/A"
        endpoint    = _truncate(r["label"], col_w["endpoint"])
        response    = _truncate(r["body_preview"] or r.get("body_preview", ""), col_w["response"])

        row = _row(i, mark, status_str, elapsed_str, endpoint, response)
        print(colour + row + RESET)

    print(sep)
    print()


# ── endpoint definitions ───────────────────────────────────────────────────────

ENDPOINTS = [
    # ── BIL /query ─────────────────────────────────────────────────────────────
    ("query.by_id",
     f"{BIL_API}/query?bildid={BILDID}"),

    ("query.by_directory",
     f"{BIL_API}/query?bildirectory={DIRECTORY}"),

    ("query.by_affiliation",
     f"{BIL_API}/query?affiliation=Carnegie+Mellon+University"),

    ("query.by_text (fulltext)",
     f"{BIL_API}/query/fulltext?text=mouse+cortex"),

    ("query.by_version (v2.0)",
     f"{BIL_API}/query?metadata=2.0"),

    # ── BIL /retrieve ──────────────────────────────────────────────────────────
    ("retrieve.by_id",
     f"{BIL_API}/retrieve?bildid={BILDID}"),

    ("retrieve.by_directory",
     f"{BIL_API}/retrieve?bildirectory={DIRECTORY}"),

    ("retrieve.by_affiliation",
     f"{BIL_API}/retrieve?affiliation=Carnegie+Mellon+University"),

    # ── metadata.get (uses /retrieve) ──────────────────────────────────────────
    ("metadata.get",
     f"{BIL_API}/retrieve?bildid={BILDID}"),

    # ── inventory (download server) ────────────────────────────────────────────
    ("inventory.get / inventory.exists  [HEAD]",
     f"{DOWNLOAD}/inventory/datasets/JSON/{BILDID}.json.gz"),

    ("inventory.get  [GET .json.gz]",
     f"{DOWNLOAD}/inventory/datasets/JSON/{BILDID}.json.gz"),

    # ── DataCite ───────────────────────────────────────────────────────────────
    ("datecite._doi_exists / dataset.get",
     f"{DATACITE}/dois/{DOI}"),

    ("datecite._get_citations_from_datacite",
     f"{DATACITE}/dois/{DOI}/citations"),

    # ── OpenCitations ──────────────────────────────────────────────────────────
    ("datecite._get_number_of_citations_from_opencitations",
     f"{OPENCITE}/index/coci/api/v1/citation-count/{DOI}"),

    ("datecite._get_citations_from_opencitations",
     f"{OPENCITE}/index/coci/api/v1/citations/{DOI}"),

    # ── Crossref ───────────────────────────────────────────────────────────────
    ("datecite._get_title_for_doi (Crossref works)",
     f"{CROSSREF}/works/{DOI}"),

    ("datecite._get_citations_from_crossref",
     f"{CROSSREF}/works?filter=cites:{DOI}"),

    # ── Semantic Scholar ───────────────────────────────────────────────────────
    ("datecite._get_number_of_citations_from_semanticscholar",
     f"{SEMSCHOLAR}/graph/v1/paper/DOI:{DOI}?fields=citationCount"),

    ("datecite._get_citations_from_semanticscholar",
     f"{SEMSCHOLAR}/graph/v1/paper/DOI:{DOI}/citations?fields=title,authors,year,externalIds"),
]


# ── main ───────────────────────────────────────────────────────────────────────

def main() -> int:
    print("=" * 70)
    print("  brainimagelibrary — endpoint accessibility report")
    print(f"  Sample bildid : {BILDID}")
    print(f"  Sample DOI    : {DOI}")
    print("=" * 70)
    print()

    results = []
    for label, url in ENDPOINTS:
        method = "HEAD" if "HEAD" in label else "GET"
        results.append(_check(label, url, method=method))

    _print_table(results)

    total  = len(results)
    passed = sum(1 for r in results if r["ok"] and r["has_body"])
    warned = sum(1 for r in results if r["ok"] and not r["has_body"])
    failed = sum(1 for r in results if not r["ok"])

    print(f"  TOTAL: {total}  |  PASS: {passed}  |  WARN (ok but empty): {warned}  |  FAIL: {failed}")
    print()

    if failed:
        print("Failed endpoints:")
        for r in results:
            if not r["ok"]:
                print(f"  - [{r['status'] or 'N/A'}] {r['label']}")
                print(f"    {r['url']}")
                print(f"    {r['body_preview']}")
        print()

    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
