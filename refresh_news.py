#!/usr/bin/env python3
"""Refresh title + source + link + publication-date metadata from publisher RSS feeds.

No API keys or subscriptions. RSS feeds and their availability/terms may change.
This script does not copy article bodies, images, or publisher summaries.
"""
from __future__ import annotations

import datetime as dt
import email.utils
import json
import pathlib
import re
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

ROOT = pathlib.Path(__file__).resolve().parent
OUTPUT = ROOT / "news-feed.json"
SOURCES = (
    ("CNBC", "https://www.cnbc.com/id/100003114/device/rss/rss.html", ("cnbc.com",)),
    ("CNBC", "https://www.cnbc.com/id/10000664/device/rss/rss.html", ("cnbc.com",)),
    ("MarketWatch", "https://feeds.content.dowjones.io/public/rss/mw_topstories", ("marketwatch.com",)),
    ("BBC Business", "https://feeds.bbci.co.uk/news/business/rss.xml", ("bbc.com", "bbc.co.uk")),
    ("WSJ", "https://feeds.a.dj.com/rss/RSSMarketsMain.xml", ("wsj.com",)),
    ("Federal Reserve", "https://www.federalreserve.gov/feeds/press_all.xml", ("federalreserve.gov",)),
    ("BLS", "https://www.bls.gov/feed/bls_latest.rss", ("bls.gov",)),
)

MAX_DAYS_OLD = 21
MAX_ARTICLES = 240
NS = {"atom": "http://www.w3.org/2005/Atom", "dc": "http://purl.org/dc/elements/1.1/"}


def text_value(item: ET.Element, names: tuple[str, ...]) -> str:
    for name in names:
        child = item.find(name, NS)
        if child is not None and child.text:
            return re.sub(r"\s+", " ", child.text).strip()
    return ""


def parse_date(value: str) -> dt.datetime | None:
    if not value:
        return None
    try:
        date = email.utils.parsedate_to_datetime(value)
        if date and date.tzinfo is None:
            date = date.replace(tzinfo=dt.timezone.utc)
        return date.astimezone(dt.timezone.utc)
    except (ValueError, TypeError, OverflowError):
        pass
    try:
        return dt.datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(dt.timezone.utc)
    except (ValueError, TypeError):
        return None


def allowed_url(value: str, hosts: tuple[str, ...]) -> str | None:
    try:
        parsed = urllib.parse.urlsplit(value.strip())
        host = (parsed.hostname or "").lower()
        if parsed.scheme != "https" or not any(host == h or host.endswith("." + h) for h in hosts):
            return None
        if parsed.username or parsed.password:
            return None
        # UTM parameters can create duplicate links, but otherwise preserve original publisher URL.
        return urllib.parse.urlunsplit((parsed.scheme, parsed.netloc, parsed.path, parsed.query, ""))
    except ValueError:
        return None


def classify(title: str, source: str) -> str:
    line = title.lower()
    if source == "Federal Reserve" or re.search(r"\bfed\b|fomc|powell|warsh|interest rates?|rate cuts?|rate hikes?|treasury yields?|bond yields?", line):
        return "Fed / Rates"
    if re.search(r"\b(stock|stocks|wall street|market|markets|s&p|nasdaq|dow jones|rally|selloff|share price|equities|trading)\b", line):
        return "Markets"
    if re.search(r"\b(inflation|cpi|pce|payroll|unemployment|jobs|gdp|economic|consumer|retail|housing|manufactur|recession|tariff|ism|job openings|jolts)\b", line):
        return "Economy"
    if re.search(r"\b(earnings|revenue|profit|ceo|merger|acquisition|tesla|nvidia|alphabet|apple|microsoft|meta|amazon|company|companies|chipmaker|ai)\b", line):
        return "Companies"
    if re.search(r"\b(china|europe|global|ukraine|russia|asia|japan|middle east|world|trade war|opec)\b", line):
        return "World"
    return "Other"


def parse_feed(payload: bytes, source: str, hosts: tuple[str, ...], now: dt.datetime) -> list[dict]:
    doc = ET.fromstring(payload)
    items = list(doc.findall(".//item"))
    if not items:
        items = list(doc.findall("atom:entry", NS))
    found = []
    for item in items[:65]:
        title = text_value(item, ("title", "atom:title"))[:230]
        url = text_value(item, ("link",))
        if not url:
            link = item.find("atom:link", NS)
            if link is not None:
                url = link.get("href") or ""
        url = allowed_url(url, hosts)
        timestamp = parse_date(text_value(item, ("pubDate", "atom:published", "atom:updated", "dc:date")))
        # Don't pretend an undated entry is fresh, and avoid stale/scheduled future entries.
        if not title or not url or timestamp is None:
            continue
        if timestamp > now + dt.timedelta(hours=3) or timestamp < now - dt.timedelta(days=MAX_DAYS_OLD):
            continue
        found.append({"title": title, "url": url, "source": source,
                      "topic": classify(title, source), "published_utc": timestamp.isoformat(timespec="seconds")})
    return found


def download(url: str) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (compatible; StreamsIntoWealthNewsIndex/1.0; headlines and links only)", "Accept": "application/rss+xml, application/atom+xml, text/xml, application/xml, */*"})
    with urllib.request.urlopen(request, timeout=18) as response:
        data = response.read(2_000_000)
    return data


def refresh() -> int:
    now = dt.datetime.now(dt.timezone.utc)
    collected: list[dict] = []
    sources_ok = 0
    for source, endpoint, hosts in SOURCES:
        try:
            items = parse_feed(download(endpoint), source, hosts, now)
            print(f"{source}: {len(items)} recent items")
            if items:
                sources_ok += 1
                collected.extend(items)
        except Exception as exc:  # Individual publisher feeds often change or block requests.
            print(f"WARNING: {source} feed failed: {type(exc).__name__}: {exc}")
    if sources_ok == 0:
        print("No source produced valid recent articles; preserving previous verified feed.")
        return 1
    seen_titles = set()
    clean = []
    for article in sorted(collected, key=lambda a:a["published_utc"], reverse=True):
        key = re.sub(r"\W+", " ", article["title"].lower()).strip()
        if not key or key in seen_titles:
            continue
        clean.append(article)
        seen_titles.add(key)
        if len(clean) == MAX_ARTICLES:
            break
    previous = {}
    if OUTPUT.exists():
        try:
            previous = json.loads(OUTPUT.read_text(encoding="utf-8"))
        except (ValueError, OSError):
            previous = {}
    # Do not create commits every hour if the actual article list is unchanged.
    if previous.get("articles") == clean:
        print("No headline changes. Keeping prior successful update timestamp.")
        return 0
    payload = {"updated_utc": now.isoformat(timespec="seconds"), "articles": clean}
    OUTPUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    print(f"Wrote {len(clean)} verified headline metadata entries to {OUTPUT.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(refresh())
