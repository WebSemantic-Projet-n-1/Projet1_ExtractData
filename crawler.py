#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
import json
import time
import hashlib
from dataclasses import dataclass, field
from typing import Iterable, Optional, Set, List, Tuple, Dict
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

from rdflib import Graph


JSONLD_MIME = "application/ld+json"


def _is_url(s: str) -> bool:
    return bool(re.match(r"^https?://", s.strip(), flags=re.IGNORECASE))


def _read_text_file(path: str, encoding: str = "utf-8") -> str:
    with open(path, "r", encoding=encoding, errors="ignore") as f:
        return f.read()


def _sha1(text: str) -> str:
    return hashlib.sha1(text.encode("utf-8", errors="ignore")).hexdigest()


def extract_jsonld_blocks(html: str) -> List[str]:
    """
    Retourne la liste des contenus JSON-LD trouvés (brut, chaîne JSON).
    Gère:
      - 1 ou plusieurs <script type="application/ld+json">
      - JSON objet, JSON array, ou plusieurs objets concaténés (rare, mais arrive)
    """
    soup = BeautifulSoup(html, "html.parser")
    blocks = []
    for tag in soup.find_all("script", attrs={"type": JSONLD_MIME}):
        if not tag.string:
            # parfois le contenu est dans .text
            content = tag.get_text(strip=False)
        else:
            content = tag.string

        if content:
            content = content.strip()
            if content:
                blocks.append(content)
    return blocks


def safe_parse_jsonld(block: str) -> List[dict]:
    """
    Parse un bloc JSON-LD et retourne une liste d'objets JSON (dict).
    - Si c'est un objet -> [obj]
    - Si c'est une liste -> la liste
    - Si c'est invalid JSON (ex: plusieurs objets) -> tentative de récupération
    """
    block = block.strip()

    # Tentative standard
    try:
        obj = json.loads(block)
        if isinstance(obj, list):
            return [x for x in obj if isinstance(x, dict)]
        if isinstance(obj, dict):
            return [obj]
        return []
    except json.JSONDecodeError:
        pass

    # Fallback: certains sites concatènent plusieurs objets JSON sans array
    # ex: {...}\n{...}
    recovered = []
    # Heuristique simple: séparer sur des occurrences "}\s*{"
    parts = re.split(r"}\s*{", block)
    if len(parts) <= 1:
        return []

    for i, p in enumerate(parts):
        if i == 0:
            p = p + "}"
        elif i == len(parts) - 1:
            p = "{" + p
        else:
            p = "{" + p + "}"
        try:
            o = json.loads(p)
            if isinstance(o, dict):
                recovered.append(o)
        except json.JSONDecodeError:
            continue
    return recovered


def add_jsonld_to_graph(g: Graph, jsonld_obj: dict, base_iri: Optional[str] = None) -> int:
    """
    Ajoute un objet JSON-LD (dict) au graphe RDFLib.
    On sérialise en JSON string puis parse via rdflib en 'json-ld'.
    """
    data = json.dumps(jsonld_obj, ensure_ascii=False)
    before = len(g)
    # base est utile si JSON-LD contient des @id relatifs
    g.parse(data=data, format="json-ld", publicID=base_iri)
    return len(g) - before


@dataclass
class CrawlStats:
    pages_seen: int = 0
    pages_parsed: int = 0
    jsonld_blocks: int = 0
    jsonld_objects: int = 0
    triples_added: int = 0
    errors: List[Tuple[str, str]] = field(default_factory=list)


class JsonLdCrawler:
    """
    Crawler JSON-LD :
    - source peut être un dossier local (site exporté) ou une URL.
    - si URL: crawl basique en suivant les liens internes (BFS),
      avec limites (max_pages, same_domain).
    """

    def __init__(
        self,
        source: str,
        max_pages: int = 200,
        same_domain: bool = True,
        timeout: int = 15,
        sleep_sec: float = 0.0,
        user_agent: str = "JsonLdCrawler/1.0 (course project)",
    ):
        self.source = source
        self.max_pages = max_pages
        self.same_domain = same_domain
        self.timeout = timeout
        self.sleep_sec = sleep_sec
        self.headers = {"User-Agent": user_agent}

        self.graph = Graph()
        self.stats = CrawlStats()

        # Pour éviter de re-parser la même page
        self._visited: Set[str] = set()
        self._visited_hashes: Set[str] = set()

        # Domaine de référence si URL
        self._base_domain = None
        if _is_url(source):
            self._base_domain = urlparse(source).netloc.lower()

    # -----------------------------
    # Local crawl (dossier)
    # -----------------------------
    def crawl_local_folder(self, folder: str, exts: Tuple[str, ...] = (".html", ".htm")) -> Graph:
        paths = []
        for root, _, files in os.walk(folder):
            for fn in files:
                if fn.lower().endswith(exts):
                    paths.append(os.path.join(root, fn))

        # Limite max_pages
        paths = paths[: self.max_pages]

        for path in paths:
            self.stats.pages_seen += 1
            try:
                html = _read_text_file(path)
                # anti-doublon par hash de contenu
                h = _sha1(html)
                if h in self._visited_hashes:
                    continue
                self._visited_hashes.add(h)

                base_iri = None
                # base IRI "file://..." utile pour @id relatifs
                try:
                    base_iri = "file://" + os.path.abspath(path)
                except Exception:
                    base_iri = None

                self._parse_html_and_add_jsonld(html, base_iri=base_iri, page_id=path)
                self.stats.pages_parsed += 1
            except Exception as e:
                self.stats.errors.append((path, repr(e)))

        return self.graph

    # -----------------------------
    # Web crawl (URL)
    # -----------------------------
    def crawl_web(self, start_url: str) -> Graph:
        queue: List[str] = [start_url]

        while queue and len(self._visited) < self.max_pages:
            url = queue.pop(0)
            if url in self._visited:
                continue
            self._visited.add(url)
            self.stats.pages_seen += 1

            try:
                r = requests.get(url, headers=self.headers, timeout=self.timeout)
                r.raise_for_status()
                html = r.text

                # anti-doublon contenu
                h = _sha1(html)
                if h in self._visited_hashes:
                    continue
                self._visited_hashes.add(h)

                self._parse_html_and_add_jsonld(html, base_iri=url, page_id=url)
                self.stats.pages_parsed += 1

                # extraire liens internes
                for link in self._extract_links(html, base_url=url):
                    if link not in self._visited and self._allowed(link):
                        queue.append(link)

                if self.sleep_sec > 0:
                    time.sleep(self.sleep_sec)

            except Exception as e:
                self.stats.errors.append((url, repr(e)))

        return self.graph

    def _allowed(self, url: str) -> bool:
        if not self.same_domain or not self._base_domain:
            return True
        return urlparse(url).netloc.lower() == self._base_domain

    def _extract_links(self, html: str, base_url: str) -> Set[str]:
        soup = BeautifulSoup(html, "html.parser")
        out: Set[str] = set()
        for a in soup.find_all("a", href=True):
            href = a.get("href", "").strip()
            if not href or href.startswith("#"):
                continue
            abs_url = urljoin(base_url, href)
            # garder http(s)
            if _is_url(abs_url):
                out.add(abs_url.split("#")[0])
        return out

    # -----------------------------
    # Parsing JSON-LD
    # -----------------------------
    def _parse_html_and_add_jsonld(self, html: str, base_iri: Optional[str], page_id: str) -> None:
        blocks = extract_jsonld_blocks(html)
        self.stats.jsonld_blocks += len(blocks)

        for block in blocks:
            objs = safe_parse_jsonld(block)
            self.stats.jsonld_objects += len(objs)

            for obj in objs:
                try:
                    added = add_jsonld_to_graph(self.graph, obj, base_iri=base_iri)
                    self.stats.triples_added += added
                except Exception as e:
                    self.stats.errors.append((page_id, f"JSON-LD parse error: {repr(e)}"))


def main():
    """
    Exemples:
    1) Crawler un dossier local :
        python jsonld_crawler.py "/chemin/vers/site_enriched"
    2) Crawler un site web :
        python jsonld_crawler.py "https://example.com"
    """
    # import sys

    # if len(sys.argv) < 2:
    #     print("Usage: python jsonld_crawler.py <folder_or_url> [out_ttl]")
    #     sys.exit(1)

    # source = sys.argv[1]
    source = "web_3.0_jsonld_output" 
    # out_ttl = sys.argv[2] if len(sys.argv) >= 3 else "knowledge_graph.ttl"
    out_ttl = "knowledge_graph.ttl"

    crawler = JsonLdCrawler(source=source, max_pages=500, same_domain=True)

    if _is_url(source):
        g = crawler.crawl_web(source)
    else:
        g = crawler.crawl_local_folder(source)

    # Sauvegarde
    g.serialize(destination=out_ttl, format="turtle")

    # Stats
    print("\n=== Crawl stats ===")
    print("Pages vues       :", crawler.stats.pages_seen)
    print("Pages parsées    :", crawler.stats.pages_parsed)
    print("Blocs JSON-LD    :", crawler.stats.jsonld_blocks)
    print("Objets JSON-LD   :", crawler.stats.jsonld_objects)
    print("Triples ajoutés  :", crawler.stats.triples_added)
    print("Triples total    :", len(g))
    print("Erreurs          :", len(crawler.stats.errors))
    if crawler.stats.errors:
        print("\n--- Exemples d'erreurs (max 10) ---")
        for where, err in crawler.stats.errors[:10]:
            print("-", where, "=>", err)

    print(f"\nGraphe exporté en Turtle: {out_ttl}")


if __name__ == "__main__":
    main()
