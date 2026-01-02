"""Citation agent using Gemini or Upstage with function calling."""

import json
from typing import List, Dict, Tuple, Optional
import google.generativeai as genai
from openai import OpenAI

from .paper_search import PaperSearcher, Paper, generate_bibtex_entry, generate_bibtex_key


class CitationAgent:
    """Agent that adds citations to LaTeX text using LLM and paper search."""

    def __init__(self, provider: str = "gemini", api_key: str = "",
                 base_url: str = "https://api.upstage.ai/v1",
                 model: str = "gemini-2.0-flash-exp", temperature: float = 0.3,
                 semantic_scholar_api_key: Optional[str] = None):
        """
        Initialize the citation agent.

        Args:
            provider: LLM provider ("gemini" or "upstage")
            api_key: API key for the chosen provider
            base_url: API base URL (for Upstage)
            model: Model name to use
            temperature: Sampling temperature
            semantic_scholar_api_key: Optional Semantic Scholar API key
        """
        self.provider = provider.lower()
        self.model = model
        self.temperature = temperature
        self.paper_searcher = PaperSearcher(api_key=semantic_scholar_api_key)

        # Initialize the appropriate client
        if self.provider == "gemini":
            genai.configure(api_key=api_key)
            self.client = genai.GenerativeModel(
                model_name=model,
                generation_config={
                    "temperature": temperature,
                }
            )
        else:  # upstage
            self.client = OpenAI(api_key=api_key, base_url=base_url)

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

    def _create_tools_definition(self) -> List:
        """Create tool definitions for function calling."""
        if self.provider == "gemini":
            # Gemini function declaration format
            return [
                genai.protos.Tool(
                    function_declarations=[
                        genai.protos.FunctionDeclaration(
                            name="search_paper",
                            description=(
                                "Search for academic papers based on a query. "
                                "Use this when you identify ANY claim, model, method, or concept that needs citation. "
                                "Extract key concepts from the claim to form a CONCISE search query (MAX 3 WORDS). "
                                "You can and SHOULD call this multiple times for different concepts in the text."
                            ),
                            parameters=genai.protos.Schema(
                                type=genai.protos.Type.OBJECT,
                                properties={
                                    "query": genai.protos.Schema(
                                        type=genai.protos.Type.STRING,
                                        description="Search keywords - MAX 3 WORDS (e.g., 'WavLM speech', 't-SNE visualization', 'PCA analysis')"
                                    ),
                                    "limit": genai.protos.Schema(
                                        type=genai.protos.Type.INTEGER,
                                        description="Maximum number of papers to return (default: 5, increase to 10 for important concepts)"
                                    )
                                },
                                required=["query"]
                            )
                        ),
                        genai.protos.FunctionDeclaration(
                            name="get_bibtex",
                            description=(
                                "Get the BibTeX entry for a specific paper using its citation key. "
                                "Use this after selecting the most relevant paper from search results."
                            ),
                            parameters=genai.protos.Schema(
                                type=genai.protos.Type.OBJECT,
                                properties={
                                    "paper_key": genai.protos.Schema(
                                        type=genai.protos.Type.STRING,
                                        description="The citation key of the paper (e.g., 'vaswani2017attention')"
                                    )
                                },
                                required=["paper_key"]
                            )
                        )
                    ]
                )
            ]
        else:
            # OpenAI format for Upstage
            return [
                {
                    "type": "function",
                    "function": {
                        "name": "search_paper",
                        "description": (
                            "Search for academic papers based on a query. "
                            "Use this when you identify ANY claim, model, method, or concept that needs citation. "
                            "Extract key concepts from the claim to form a CONCISE search query (MAX 3 WORDS). "
                            "You can and SHOULD call this multiple times for different concepts in the text."
                        ),
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "query": {
                                    "type": "string",
                                    "description": "Search keywords - MAX 3 WORDS (e.g., 'WavLM speech', 't-SNE visualization', 'PCA analysis')"
                                },
                                "limit": {
                                    "type": "integer",
                                    "description": "Maximum number of papers to return (default: 5, increase to 10 for important concepts)",
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
        print(f"CITATION AGENT: Processing LaTeX Text (Provider: {self.provider})")
        print("="*60)

        if self.provider == "gemini":
            return self._process_text_gemini(latex_text, context)
        else:
            return self._process_text_upstage(latex_text, context)

    def _process_text_gemini(self, latex_text: str, context: str = "") -> Tuple[str, List[str]]:
        """Process text using Gemini API."""
        # Construct instruction
        instruction = (
            "You are an academic research assistant specialized in adding citations to LaTeX documents. "
            "Your task is to:\n"
            "1. **THOROUGHLY** identify ALL claims, statements, facts, models, methods, or concepts that need citations\n"
            "2. Search for relevant academic papers using search_paper tool with CONCISE queries (MAX 3 WORDS)\n"
            "3. Select the most appropriate paper(s) from search results\n"
            "4. **IMPORTANT**: MUST call get_bibtex tool ONCE for EACH selected paper (ONE paper_key per call)\n"
            "5. Insert \\cite{key} or \\cite{key1,key2,key3} tags at appropriate positions\n\n"
            "**SEARCH QUERY RULES**:\n"
            "- Keep search queries SHORT - maximum 3 words\n"
            "- Use key terms only (e.g., 'WavLM', 't-SNE visualization', 'PCA analysis')\n"
            "- DO NOT use full paper titles or long descriptions\n"
            "- Call search_paper multiple times with different short queries if needed\n\n"
            "**CRITICAL CITATION REQUIREMENTS**:\n"
            "- **DO NOT add citations to \\begin{abstract}...\\end{abstract} sections**\n"
            "- Add citations for EVERY factual claim in the main text, not just at the end of sentences\n"
            "- When mentioning specific models (e.g., 'WavLM', 'BERT', 'GPT'), cite the original paper\n"
            "- When mentioning specific methods (e.g., 'PCA', 'orthogonal projection'), cite foundational or recent papers\n"
            "- When mentioning datasets, benchmarks, or evaluation metrics, cite the papers that introduced them\n"
            "- Use multiple citations \\cite{paper1,paper2,paper3} when a claim is supported by multiple works\n"
            "- Add citations in the MIDDLE of sentences when specific concepts are introduced\n"
            "- Add citations IMMEDIATELY after mentioning a model/method name, not just at sentence end\n\n"
            "**Citation Style Guidelines**:\n"
            "- Use \\cite{} for all citations: Some work has been done~\\cite{author2020}\n"
            "- Use \\cite{key1,key2,key3} for multiple citations: This is well-known~\\cite{author2020,smith2021,jones2022}\n"
            "- Always use \\cite{} consistently (not \\citep or \\citet)\n"
            "- Prefer highly-cited, recent papers from reputable venues\n\n"
            "**Examples of GOOD citation placement**:\n"
            "✓ \"WavLM~\\cite{chen2022wavlm} is a self-supervised model that...\"\n"
            "✓ \"Recent work on speech synthesis~\\cite{wang2023,li2024,zhang2024} has shown...\"\n"
            "✓ \"We use t-SNE~\\cite{maaten2008visualizing} and UMAP~\\cite{mcinnes2018umap} for visualization\"\n"
            "✓ \"The model suffers from overfitting~\\cite{zhang2021understanding,kumar2022generalization}\"\n\n"
            "**Examples of BAD citation placement**:\n"
            "✗ \"WavLM is a self-supervised model that captures acoustic features.\" (Missing citation for WavLM)\n"
            "✗ \"We use PCA for dimensionality reduction.\" (Missing citation for PCA methodology)\n"
            "✗ \"This approach has been studied extensively.\" (Vague - needs specific citations)\n\n"
            "**CRITICAL**: You MUST call get_bibtex for EVERY paper you want to cite. Do NOT make up citation keys.\n"
            "Do NOT modify the text content itself, ONLY add citation commands.\n"
            "Return ONLY the modified text with citations, without explanations."
        )

        if context:
            instruction += f"\n\nDocument context: {context}"

        user_message = (
            "Please add COMPREHENSIVE citations to this LaTeX text. "
            "Identify EVERY claim, model name, method, dataset, and concept that needs citation. "
            "Use multiple citations when appropriate (e.g., \\cite{paper1,paper2,paper3}). "
            "Add citations in the MIDDLE of sentences when specific concepts are introduced, "
            "not just at the end of sentences.\n\n"
            f"LaTeX text to process:\n\n{latex_text}"
        )

        tools = self._create_tools_definition()
        collected_bibtex = []

        # Initialize chat with tools
        chat = self.client.start_chat(enable_automatic_function_calling=False)

        # First call
        print("\n[Agent] Analyzing text and planning citations...")
        response = chat.send_message(
            f"{instruction}\n\n{user_message}",
            tools=tools
        )

        # Handle function calls
        max_iterations = 10
        iteration = 0

        while iteration < max_iterations:
            # Check for errors in response
            if response.candidates[0].finish_reason.name in ["MALFORMED_FUNCTION_CALL", "SAFETY", "RECITATION"]:
                print(f"\n[Agent] Warning: Response stopped due to: {response.candidates[0].finish_reason.name}")
                print("[Agent] Attempting to continue with current citations...")
                break

            if not response.candidates[0].content.parts:
                break

            # Check for function calls
            function_calls = [part.function_call for part in response.candidates[0].content.parts if part.function_call.name]

            if not function_calls:
                # No more function calls, get final text
                break

            # Execute all function calls
            function_responses = []
            for fc in function_calls:
                function_name = fc.name
                function_args = dict(fc.args)

                print(f"\n[Agent] Calling tool: {function_name}")
                print(f"[Agent] Arguments: {function_args}")

                if function_name == "search_paper":
                    result = self._search_paper_tool(
                        query=function_args.get("query"),
                        limit=function_args.get("limit", 5)
                    )
                elif function_name == "get_bibtex":
                    # Handle both 'paper_key' (correct) and 'keys' (incorrect but common mistake)
                    paper_key = function_args.get("paper_key")

                    # If Gemini sends a 'keys' parameter (list or string), handle it
                    if paper_key is None and "keys" in function_args:
                        try:
                            keys_value = function_args.get("keys")

                            # Convert to list if needed
                            if isinstance(keys_value, str):
                                import json as json_lib
                                keys_list = json_lib.loads(keys_value)
                            elif isinstance(keys_value, list):
                                keys_list = keys_value
                            else:
                                # Handle protobuf RepeatedComposite by converting to list
                                keys_list = list(keys_value)

                            print(f"[Agent] Processing {len(keys_list)} paper keys")

                            # Call get_bibtex for each key
                            results = []
                            for key in keys_list:
                                bibtex_result = self._get_bibtex_tool(paper_key=str(key))
                                collected_bibtex.append(bibtex_result)
                                results.append(bibtex_result)

                            result = "\n\n".join(results)
                        except Exception as e:
                            print(f"[Agent] Error parsing keys: {e}")
                            import traceback
                            traceback.print_exc()
                            result = "Error: Invalid keys format. Please call get_bibtex once for each paper_key individually."
                    elif paper_key:
                        result = self._get_bibtex_tool(paper_key=paper_key)
                        collected_bibtex.append(result)
                    else:
                        result = "Error: No paper_key provided"
                else:
                    result = "Unknown function"

                function_responses.append(
                    genai.protos.Part(
                        function_response=genai.protos.FunctionResponse(
                            name=function_name,
                            response={"result": result}
                        )
                    )
                )

            # Send function responses back
            print("\n[Agent] Sending function results back to model...")
            try:
                response = chat.send_message(function_responses)
                iteration += 1
            except Exception as e:
                print(f"\n[Agent] Error during function call iteration: {e}")
                print("[Agent] Stopping function calling loop and using current citations...")
                break

        # Extract final text
        try:
            if response.candidates[0].content.parts:
                modified_text = response.text
            else:
                print("\n[Agent] No text in response, using original text with any citations found...")
                modified_text = latex_text
        except Exception as e:
            print(f"\n[Agent] Error extracting final text: {e}")
            print("[Agent] Using original text...")
            modified_text = latex_text

        print("\n" + "="*60)
        print("CITATION AGENT: Processing Complete")
        print("="*60)

        return modified_text, collected_bibtex

    def _process_text_upstage(self, latex_text: str, context: str = "") -> Tuple[str, List[str]]:
        """Process text using Upstage API (OpenAI-compatible)."""
        # Construct system message
        system_message = (
            "You are an academic research assistant specialized in adding citations to LaTeX documents. "
            "Your task is to:\n"
            "1. **THOROUGHLY** identify ALL claims, statements, facts, models, methods, or concepts that need citations\n"
            "2. Search for relevant academic papers using search_paper tool with CONCISE queries (MAX 3 WORDS)\n"
            "3. Select the most appropriate paper(s) from search results\n"
            "4. **IMPORTANT**: MUST call get_bibtex tool ONCE for EACH selected paper (ONE paper_key per call)\n"
            "5. Insert \\cite{key} or \\cite{key1,key2,key3} tags at appropriate positions\n\n"
            "**SEARCH QUERY RULES**:\n"
            "- Keep search queries SHORT - maximum 3 words\n"
            "- Use key terms only (e.g., 'WavLM', 't-SNE visualization', 'PCA analysis')\n"
            "- DO NOT use full paper titles or long descriptions\n"
            "- Call search_paper multiple times with different short queries if needed\n\n"
            "**CRITICAL CITATION REQUIREMENTS**:\n"
            "- **DO NOT add citations to \\begin{abstract}...\\end{abstract} sections**\n"
            "- Add citations for EVERY factual claim in the main text, not just at the end of sentences\n"
            "- When mentioning specific models (e.g., 'WavLM', 'BERT', 'GPT'), cite the original paper\n"
            "- When mentioning specific methods (e.g., 'PCA', 'orthogonal projection'), cite foundational or recent papers\n"
            "- When mentioning datasets, benchmarks, or evaluation metrics, cite the papers that introduced them\n"
            "- Use multiple citations \\cite{paper1,paper2,paper3} when a claim is supported by multiple works\n"
            "- Add citations in the MIDDLE of sentences when specific concepts are introduced\n"
            "- Add citations IMMEDIATELY after mentioning a model/method name, not just at sentence end\n\n"
            "**Citation Style Guidelines**:\n"
            "- Use \\cite{} for all citations: Some work has been done~\\cite{author2020}\n"
            "- Use \\cite{key1,key2,key3} for multiple citations: This is well-known~\\cite{author2020,smith2021,jones2022}\n"
            "- Always use \\cite{} consistently (not \\citep or \\citet)\n"
            "- Prefer highly-cited, recent papers from reputable venues\n\n"
            "**Examples of GOOD citation placement**:\n"
            "✓ \"WavLM~\\cite{chen2022wavlm} is a self-supervised model that...\"\n"
            "✓ \"Recent work on speech synthesis~\\cite{wang2023,li2024,zhang2024} has shown...\"\n"
            "✓ \"We use t-SNE~\\cite{maaten2008visualizing} and UMAP~\\cite{mcinnes2018umap} for visualization\"\n"
            "✓ \"The model suffers from overfitting~\\cite{zhang2021understanding,kumar2022generalization}\"\n\n"
            "**Examples of BAD citation placement**:\n"
            "✗ \"WavLM is a self-supervised model that captures acoustic features.\" (Missing citation for WavLM)\n"
            "✗ \"We use PCA for dimensionality reduction.\" (Missing citation for PCA methodology)\n"
            "✗ \"This approach has been studied extensively.\" (Vague - needs specific citations)\n\n"
            "**CRITICAL**: You MUST call get_bibtex for EVERY paper you want to cite. Do NOT make up citation keys.\n"
            "Do NOT modify the text content itself, ONLY add citation commands.\n"
            "Return ONLY the modified text with citations, without explanations."
        )

        if context:
            system_message += f"\n\nDocument context: {context}"

        messages = [
            {"role": "system", "content": system_message},
            {
                "role": "user",
                "content": (
                    "Please add COMPREHENSIVE citations to this LaTeX text. "
                    "Identify EVERY claim, model name, method, dataset, and concept that needs citation. "
                    "Use multiple citations when appropriate (e.g., \\cite{paper1,paper2,paper3}). "
                    "Add citations in the MIDDLE of sentences when specific concepts are introduced, "
                    "not just at the end of sentences.\n\n"
                    f"LaTeX text to process:\n\n{latex_text}"
                )
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
