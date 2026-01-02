"""Paper search functionality using Semantic Scholar API."""

import json
import time
import requests
from typing import List, Dict, Optional
from dataclasses import dataclass


@dataclass
class Paper:
    """Represents a scientific paper."""
    paper_id: str
    title: str
    authors: List[str]
    year: Optional[int]
    citation_count: int
    doi: Optional[str]
    arxiv_id: Optional[str]
    abstract: Optional[str]

    def to_dict(self) -> Dict:
        """Convert paper to dictionary."""
        return {
            "paper_id": self.paper_id,
            "title": self.title,
            "authors": self.authors,
            "year": self.year,
            "citation_count": self.citation_count,
            "doi": self.doi,
            "arxiv_id": self.arxiv_id,
            "abstract": self.abstract
        }


class PaperSearcher:
    """Search for academic papers using Semantic Scholar API."""

    def __init__(self, base_url: str = "https://api.semanticscholar.org/graph/v1",
                 api_key: Optional[str] = None):
        self.base_url = base_url
        self.session = requests.Session()
        headers = {
            "User-Agent": "CiteAgent/0.1.0 (Academic Research Assistant)"
        }
        # Add API key if provided (optional, but helps with rate limits)
        if api_key:
            headers["x-api-key"] = api_key
        self.session.headers.update(headers)

    def search_papers(self, query: str, limit: int = 5, min_citations: int = 10) -> List[Paper]:
        """
        Search for papers matching the query.

        Args:
            query: Search query string
            limit: Maximum number of results
            min_citations: Minimum citation count filter

        Returns:
            List of Paper objects
        """
        print(f"\n[PaperSearch] Searching for: '{query}'")

        # Retry logic for rate limiting
        max_retries = 3
        retry_delay = 2  # seconds
        papers = []

        for attempt in range(max_retries):
            try:
                # Search using Semantic Scholar API
                search_url = f"{self.base_url}/paper/search"
                params = {
                    "query": query,
                    "limit": limit * 2,  # Get more results to filter
                    "fields": "title,authors,year,citationCount,paperId,externalIds,abstract"
                }

                response = self.session.get(search_url, params=params, timeout=15)

                # Handle rate limiting with retry
                if response.status_code == 429:
                    if attempt < max_retries - 1:
                        wait_time = retry_delay * (attempt + 1)
                        print(f"[PaperSearch] Rate limited. Waiting {wait_time}s before retry...")
                        time.sleep(wait_time)
                        continue
                    else:
                        print(f"[PaperSearch] Rate limit exceeded after {max_retries} attempts")
                        return []

                response.raise_for_status()

                # Parse response
                data = response.json()

                if "data" not in data:
                    print(f"[PaperSearch] No results found for query: {query}")
                    return []

                for item in data["data"]:
                    # Filter by citation count
                    if item.get("citationCount", 0) < min_citations:
                        continue

                    # Extract author names
                    authors = [author.get("name", "Unknown") for author in item.get("authors", [])]

                    # Get external IDs
                    external_ids = item.get("externalIds", {})
                    doi = external_ids.get("DOI")
                    arxiv_id = external_ids.get("ArXiv")

                    paper = Paper(
                        paper_id=item.get("paperId", ""),
                        title=item.get("title", "Unknown Title"),
                        authors=authors,
                        year=item.get("year"),
                        citation_count=item.get("citationCount", 0),
                        doi=doi,
                        arxiv_id=arxiv_id,
                        abstract=item.get("abstract", "")
                    )

                    papers.append(paper)

                    if len(papers) >= limit:
                        break

                # Success, exit retry loop
                break

            except requests.exceptions.RequestException as e:
                if attempt < max_retries - 1:
                    print(f"[PaperSearch] Request failed (attempt {attempt + 1}/{max_retries}), retrying...")
                    time.sleep(retry_delay)
                    continue
                else:
                    print(f"[PaperSearch] Error searching papers after {max_retries} attempts: {e}")
                    return []

        print(f"[PaperSearch] Found {len(papers)} papers")
        return papers

    def get_paper_details(self, paper_id: str) -> Optional[Paper]:
        """
        Get detailed information about a specific paper.

        Args:
            paper_id: Semantic Scholar paper ID

        Returns:
            Paper object or None if not found
        """
        try:
            url = f"{self.base_url}/paper/{paper_id}"
            params = {
                "fields": "title,authors,year,citationCount,paperId,externalIds,abstract"
            }

            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()

            item = response.json()

            authors = [author.get("name", "Unknown") for author in item.get("authors", [])]
            external_ids = item.get("externalIds", {})

            return Paper(
                paper_id=item.get("paperId", ""),
                title=item.get("title", "Unknown Title"),
                authors=authors,
                year=item.get("year"),
                citation_count=item.get("citationCount", 0),
                doi=external_ids.get("DOI"),
                arxiv_id=external_ids.get("ArXiv"),
                abstract=item.get("abstract", "")
            )

        except Exception as e:
            print(f"[PaperSearch] Error getting paper details: {e}")
            return None


def generate_bibtex_key(paper: Paper) -> str:
    """
    Generate a BibTeX citation key from paper metadata.

    Format: firstauthor_year_keyword
    Example: vaswani2017attention
    """
    # Get first author's last name
    first_author = paper.authors[0] if paper.authors else "unknown"
    last_name = first_author.split()[-1].lower()

    # Get year
    year = paper.year if paper.year else 2024

    # Get first significant word from title (skip common words)
    skip_words = {"the", "a", "an", "on", "of", "for", "and", "in", "to", "with"}
    title_words = [w.lower() for w in paper.title.split() if w.lower() not in skip_words]
    keyword = title_words[0] if title_words else "paper"

    # Remove non-alphanumeric characters
    keyword = ''.join(c for c in keyword if c.isalnum())
    last_name = ''.join(c for c in last_name if c.isalnum())

    return f"{last_name}{year}{keyword}"


def generate_bibtex_entry(paper: Paper) -> str:
    """
    Generate a BibTeX entry from paper metadata.

    Args:
        paper: Paper object

    Returns:
        BibTeX formatted string
    """
    key = generate_bibtex_key(paper)

    # Format authors (convert list to "Last1, First1 and Last2, First2" format)
    authors_str = " and ".join(paper.authors)

    # Determine entry type and build entry
    if paper.arxiv_id:
        entry_type = "article"
        venue = "arXiv preprint"
    elif paper.doi:
        entry_type = "article"
        venue = "Journal"
    else:
        entry_type = "misc"
        venue = "Unknown"

    bibtex = f"@{entry_type}{{{key},\n"
    bibtex += f"  title={{{paper.title}}},\n"
    bibtex += f"  author={{{authors_str}}},\n"

    if paper.year:
        bibtex += f"  year={{{paper.year}}},\n"

    if paper.doi:
        bibtex += f"  doi={{{paper.doi}}},\n"

    if paper.arxiv_id:
        bibtex += f"  journal={{arXiv preprint arXiv:{paper.arxiv_id}}},\n"

    bibtex += "}"

    return bibtex
