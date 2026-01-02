#!/usr/bin/env python3
"""
Simple test script for CiteAgent without Overleaf.
Tests the citation agent functionality with sample text.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.citation_agent import CitationAgent
from src.config import Config


def test_simple_citation():
    """Test with a simple paragraph that needs citations."""

    print("\n" + "="*70)
    print("  CiteAgent Test - Simple Citation")
    print("="*70 + "\n")

    # Sample text that needs citations
    sample_text = """
Transformers have revolutionized natural language processing by introducing
the self-attention mechanism. However, large language models often suffer
from hallucination problems, generating factually incorrect information.
"""

    print("Sample text:")
    print(sample_text)
    print("\n" + "-"*70 + "\n")

    # Load config
    try:
        config = Config("config.yaml")
    except Exception as e:
        print(f"Error loading config: {e}")
        print("Make sure config.yaml exists with your API key!")
        return

    # Initialize agent
    upstage_config = config.get_upstage_config()
    agent_config = config.get_agent_config()
    semantic_config = config.get_semantic_scholar_config()

    try:
        agent = CitationAgent(
            api_key=upstage_config["api_key"],
            base_url=upstage_config["base_url"],
            model=upstage_config["model"],
            temperature=agent_config["temperature"],
            semantic_scholar_api_key=semantic_config["api_key"] if semantic_config["api_key"] else None
        )
    except ValueError as e:
        print(f"Error: {e}")
        return

    # Process text
    print("Processing with CiteAgent...\n")
    modified_text, bibtex_entries = agent.process_text(sample_text)

    # Display results
    print("\n" + "="*70)
    print("  Results")
    print("="*70 + "\n")

    print("Modified text:")
    print(modified_text)
    print("\n" + "-"*70 + "\n")

    if bibtex_entries:
        print(f"BibTeX entries ({len(bibtex_entries)}):\n")
        for i, entry in enumerate(bibtex_entries, 1):
            print(f"Entry {i}:")
            print(entry)
            print()
    else:
        print("No citations added.")

    print("\n" + "="*70)
    print("  Test Complete!")
    print("="*70 + "\n")


def test_paper_search():
    """Test paper search functionality."""

    print("\n" + "="*70)
    print("  CiteAgent Test - Paper Search")
    print("="*70 + "\n")

    from src.paper_search import PaperSearcher, generate_bibtex_entry

    searcher = PaperSearcher()

    # Test search
    query = "transformer attention mechanism"
    print(f"Searching for: {query}\n")

    papers = searcher.search_papers(query, limit=3)

    if papers:
        print(f"Found {len(papers)} papers:\n")
        for i, paper in enumerate(papers, 1):
            print(f"{i}. {paper.title}")
            print(f"   Authors: {', '.join(paper.authors[:3])}")
            print(f"   Year: {paper.year}")
            print(f"   Citations: {paper.citation_count}")
            print()

        # Generate BibTeX for first paper
        print("-"*70 + "\n")
        print("BibTeX entry for first paper:")
        print(generate_bibtex_entry(papers[0]))
    else:
        print("No papers found.")

    print("\n" + "="*70)
    print("  Test Complete!")
    print("="*70 + "\n")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Test CiteAgent functionality")
    parser.add_argument(
        '--test',
        choices=['citation', 'search', 'all'],
        default='all',
        help='Which test to run'
    )

    args = parser.parse_args()

    if args.test in ['search', 'all']:
        test_paper_search()

    if args.test in ['citation', 'all']:
        test_simple_citation()
