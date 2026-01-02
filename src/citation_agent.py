"""Citation agent using Upstage Solar Pro 2 with function calling."""

import json
from typing import List, Dict, Tuple, Optional
from openai import OpenAI

from .paper_search import PaperSearcher, Paper, generate_bibtex_entry, generate_bibtex_key


class CitationAgent:
    """Agent that adds citations to LaTeX text using LLM and paper search."""

    def __init__(self, api_key: str, base_url: str = "https://api.upstage.ai/v1",
                 model: str = "solar-pro2", temperature: float = 0.3,
                 semantic_scholar_api_key: Optional[str] = None):
        """
        Initialize the citation agent.

        Args:
            api_key: Upstage API key
            base_url: API base URL
            model: Model name to use
            temperature: Sampling temperature
            semantic_scholar_api_key: Optional Semantic Scholar API key
        """
        self.client = OpenAI(api_key=api_key, base_url=base_url)
        self.model = model
        self.temperature = temperature
        self.paper_searcher = PaperSearcher(api_key=semantic_scholar_api_key)

        # Cache for searched papers to avoid duplicate searches
        self.paper_cache: Dict[str, List[Paper]] = {}
        self.bibtex_cache: Dict[str, str] = {}

    def _search_paper_tool(self, query: str, limit: int = 5) -> str:
        """
        Tool function: Search for papers.

        Args:
            query: Search query
            limit: Maximum number of results

        Returns:
            JSON string of search results
        """
        # Check cache
        cache_key = f"{query}_{limit}"
        if cache_key in self.paper_cache:
            papers = self.paper_cache[cache_key]
            print(f"[Agent] Using cached results for: {query}")
        else:
            papers = self.paper_searcher.search_papers(query, limit=limit)
            self.paper_cache[cache_key] = papers

        # Convert to simplified format for LLM
        results = []
        for paper in papers:
            key = generate_bibtex_key(paper)
            results.append({
                "key": key,
                "title": paper.title,
                "authors": paper.authors[:3],  # First 3 authors
                "year": paper.year,
                "citations": paper.citation_count,
                "abstract": paper.abstract[:200] if paper.abstract else ""  # First 200 chars
            })

        return json.dumps(results, ensure_ascii=False, indent=2)

    def _get_bibtex_tool(self, paper_key: str) -> str:
        """
        Tool function: Get BibTeX entry for a paper.

        Args:
            paper_key: Citation key of the paper

        Returns:
            BibTeX entry as string
        """
        # Check cache
        if paper_key in self.bibtex_cache:
            print(f"[Agent] Using cached BibTeX for: {paper_key}")
            return self.bibtex_cache[paper_key]

        # Find paper in cache by matching key
        for papers in self.paper_cache.values():
            for paper in papers:
                if generate_bibtex_key(paper) == paper_key:
                    bibtex = generate_bibtex_entry(paper)
                    self.bibtex_cache[paper_key] = bibtex
                    return bibtex

        return f"@misc{{{paper_key},\n  title={{Paper not found}},\n  year={{2024}}\n}}"

    def _create_tools_definition(self) -> List[Dict]:
        """Create tool definitions for function calling."""
        return [
            {
                "type": "function",
                "function": {
                    "name": "search_paper",
                    "description": (
                        "Search for academic papers based on a query. "
                        "Use this when you identify a claim in the text that needs citation. "
                        "Extract key concepts from the claim to form a good search query."
                    ),
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Search keywords (e.g., 'transformer attention mechanism', 'llm hallucination')"
                            },
                            "limit": {
                                "type": "integer",
                                "description": "Maximum number of papers to return (default: 5)",
                                "default": 5
                            }
                        },
                        "required": ["query"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_bibtex",
                    "description": (
                        "Get the BibTeX entry for a specific paper using its citation key. "
                        "Use this after selecting the most relevant paper from search results."
                    ),
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "paper_key": {
                                "type": "string",
                                "description": "The citation key of the paper (e.g., 'vaswani2017attention')"
                            }
                        },
                        "required": ["paper_key"]
                    }
                }
            }
        ]

    def process_text(self, latex_text: str, context: str = "") -> Tuple[str, List[str]]:
        """
        Process LaTeX text and add citations.

        Args:
            latex_text: The LaTeX text to process
            context: Additional context about the document (optional)

        Returns:
            Tuple of (modified_text, list_of_bibtex_entries)
        """
        print("\n" + "="*60)
        print("CITATION AGENT: Processing LaTeX Text")
        print("="*60)

        # Construct system message
        system_message = (
            "You are an academic research assistant specialized in adding citations to LaTeX documents. "
            "Your task is to:\n"
            "1. Identify claims, statements, or facts that need citations\n"
            "2. Search for relevant academic papers using the search_paper tool\n"
            "3. Select the most appropriate paper(s) from search results\n"
            "4. **IMPORTANT**: MUST call get_bibtex tool for EACH selected paper to get the BibTeX entry\n"
            "5. Insert \\citep{key} or \\citet{key} tags at appropriate positions\n\n"
            "Guidelines:\n"
            "- Use \\citep{} for parenthetical citations: (Author et al., 2020)\n"
            "- Use \\citet{} for textual citations: Author et al. (2020)\n"
            "- Only add citations where they are truly needed (factual claims, specific methods, etc.)\n"
            "- Prefer highly-cited, recent papers from reputable venues\n"
            "- **CRITICAL**: You MUST call get_bibtex for every paper you want to cite. Do NOT make up citation keys.\n"
            "- Do NOT modify the text content, only add citation commands\n"
            "- Return ONLY the modified text with citations, without explanations"
        )

        if context:
            system_message += f"\n\nDocument context: {context}"

        messages = [
            {"role": "system", "content": system_message},
            {
                "role": "user",
                "content": f"Please add appropriate citations to this LaTeX text:\n\n{latex_text}"
            }
        ]

        tools = self._create_tools_definition()
        collected_bibtex = []

        # First LLM call
        print("\n[Agent] Analyzing text and planning citations...")
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            tools=tools,
            tool_choice="auto",
            temperature=self.temperature
        )

        response_message = response.choices[0].message
        tool_calls = response_message.tool_calls

        # Handle tool calls
        if tool_calls:
            messages.append(response_message)

            available_functions = {
                "search_paper": self._search_paper_tool,
                "get_bibtex": self._get_bibtex_tool
            }

            for tool_call in tool_calls:
                function_name = tool_call.function.name
                function_to_call = available_functions[function_name]
                function_args = json.loads(tool_call.function.arguments)

                print(f"\n[Agent] Calling tool: {function_name}")
                print(f"[Agent] Arguments: {function_args}")

                # Execute function
                if function_name == "search_paper":
                    function_response = function_to_call(
                        query=function_args.get("query"),
                        limit=function_args.get("limit", 5)
                    )
                elif function_name == "get_bibtex":
                    paper_key = function_args.get("paper_key")
                    function_response = function_to_call(paper_key=paper_key)
                    collected_bibtex.append(function_response)

                # Add tool response to messages
                messages.append({
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": function_name,
                    "content": function_response
                })

            # Second LLM call with tool results
            print("\n[Agent] Generating final text with citations...")
            final_response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature
            )

            modified_text = final_response.choices[0].message.content

        else:
            # No tool calls needed
            print("\n[Agent] No citations needed for this text.")
            modified_text = latex_text

        print("\n" + "="*60)
        print("CITATION AGENT: Processing Complete")
        print("="*60)

        return modified_text, collected_bibtex

    def process_paragraph(self, paragraph: str) -> Tuple[str, List[str]]:
        """
        Process a single paragraph.

        Args:
            paragraph: Single paragraph of text

        Returns:
            Tuple of (modified_paragraph, list_of_bibtex_entries)
        """
        return self.process_text(paragraph)

    def clear_cache(self):
        """Clear the paper and BibTeX cache."""
        self.paper_cache.clear()
        self.bibtex_cache.clear()
        print("[Agent] Cache cleared")
