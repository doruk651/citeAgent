# CiteAgent - Automated Citation Tool for Overleaf

English | [**한국어**](README.md)

CiteAgent is an AI-powered tool that automatically adds appropriate citations to LaTeX papers being written in Overleaf.

## Key Features

- 🤖 **Gemini API** or **Upstage API** support (configurable)
- 📚 Real-time paper search via Semantic Scholar
- 🔍 Automatically selects the most relevant papers
- ✍️ Automatically inserts `\cite{}` tags in LaTeX documents
- 📝 Automatically generates BibTeX entries and adds them to mybib.bib
- 🍎 **Overleaf automation in Safari** (macOS)

## Table of Contents

- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [How It Works](#how-it-works)
- [Troubleshooting](#troubleshooting)

---

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/KyuDan1/citeAgent.git
cd citeAgent
```

### 2. Create and Activate Conda Environment

```bash
# Create conda environment (Python 3.10 or higher recommended)
conda create -n citeagent python=3.10

# Activate environment
conda activate citeagent
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Configuration

### 1. Check Configuration File

There is a `config.yaml` file in the project root. Configure your API key and LLM provider in this file.

### 2. Select LLM Provider

Open `config.yaml` and choose your LLM:

```yaml
llm:
  provider: "gemini"  # Choose "gemini" or "upstage"
```

### 3. Configure API Key

#### For Gemini API:

```yaml
llm:
  provider: "gemini"

gemini:
  api_key: "your_actual_Gemini_API_key_here"
  model: "gemini-3-flash-preview"
```

**How to get Gemini API key:**
1. Visit [Google AI Studio](https://aistudio.google.com/apikey)
2. Sign in with your Google account
3. Click "Get API Key" to create a new key
4. Copy the generated key and paste it into `config.yaml`

#### For Upstage API:

```yaml
llm:
  provider: "upstage"

upstage:
  api_key: "your_actual_Upstage_API_key_here"
  base_url: "https://api.upstage.ai/v1"
  model: "solar-pro2"
```

**How to get Upstage API key:**
1. Visit [Upstage Console](https://console.upstage.ai/)
2. Sign up or log in
3. Create a new key in the API Keys menu
4. Copy the generated key and paste it into `config.yaml`

### 4. (Optional) Semantic Scholar API Key

You can configure a Semantic Scholar API key for more API calls:

```yaml
semantic_scholar:
  api_key: ""  # Optional - works without it
```

**How to get:**
1. Visit [Semantic Scholar API](https://www.semanticscholar.org/product/api)
2. Apply for an API Key


### 5. Configure Overleaf Project URL

Set the URL of your Overleaf project:

```yaml
overleaf:
  project_url: "https://www.overleaf.com/project/your-project-id"
```

**How to find the URL:**
1. Open your project in Overleaf
2. Copy the entire URL from your browser's address bar
3. Paste it into `config.yaml`

---

## Usage

### Preparation

1. **Open Overleaf in Safari**
   - Launch Safari browser
   - Open your Overleaf project
   - Select the `.tex` file to edit
   - **Important:** Enable Safari's developer menu
     - Safari > Preferences > Advanced > Check "Show Develop menu in menu bar"

2. **Activate Conda Environment**
   ```bash
   conda activate citeagent
   ```

### Mode 1: Interactive Mode (Recommended)

Interactive mode for selecting and processing text.

```bash
python main.py --interactive
```

**Steps:**
1. **Select text in Overleaf editor that needs citations by dragging with your mouse**
2. **Press Enter in terminal**
3. Agent automatically searches for papers and adds citations
4. Results are displayed in terminal - check modified text and BibTeX
5. Choose whether to apply (`yes` to apply to Overleaf)
6. When applied:
   - Selected text is replaced with citations
   - BibTeX entries are automatically added to `mybib.bib`
7. To continue, select more text and press Enter; to exit, press `Ctrl+C`

**Example:**
```
[User] Select "WavLM is a self-supervised model" in Overleaf
[User] Press Enter in terminal
[Agent] Searching for papers...
[Agent] Found WavLM paper and generated BibTeX
[Agent] Modified text: "WavLM~\cite{chen2022wavlm} is a self-supervised model"
[User] Type "yes" to apply
[Result] Citation added in Overleaf, BibTeX entry automatically added to mybib.bib
```



**Advantages:**
- ✅ Safe (only process selected portions)
- ✅ Real-time result verification
- ✅ Prevents unwanted changes
- ✅ Easy to learn

### Mode 2: Full Document Mode

Process the entire currently open document at once.

```bash
# Apply directly to Overleaf
python main.py --full-document

# Save to file (safer)
python main.py --full-document --output modified.tex
```

**Cautions:**
- ⚠️ Entire document may be changed - **backup recommended**
- ⚠️ Processing may take time (depending on document length)
- ⚠️ Review results before applying

### Mode 3: File Mode

Process local `.tex` files without Overleaf.

```bash
python main.py --file document.tex
```

**Output:**
- `document_cited.tex` - Document with citations added
- `document_cited.bib` - BibTeX entries

**Advantages:**
- ✅ No Overleaf connection needed
- ✅ Offline work possible
- ✅ Easy version control

---

## How It Works



### Processing Steps

1. **Read Text**
   - Read text from Overleaf editor in Safari using AppleScript
   - Or read only user-selected text

2. **Analyze Text**
   - LLM (Gemini or Upstage) reads LaTeX text and identifies parts needing citations
   - **Automatically skips Abstract sections**
   - Identifies concepts needing citations: model names, methods, datasets, etc.

3. **Search Papers**
   - Search for related papers via Semantic Scholar API for identified concepts
   - Search queries are concise with **max 3 words**
   - Examples: "WavLM", "t-SNE visualization", "PCA analysis"

4. **Select Papers**
   - Select optimal papers from search results considering citation count, year, relevance
   - Prioritize highly-cited papers

5. **Generate BibTeX**
   - Automatically generate BibTeX entries from selected paper metadata
   - Comply with standard BibTeX format

6. **Insert Citations**
   - Insert `\cite{key}` tags at appropriate locations
   - For multiple papers: `\cite{key1,key2,key3}`
   - Can insert mid-sentence (e.g., "WavLM~\cite{chen2022wavlm} is...")

7. **Apply to Overleaf**
   - **Chunk-based approach** safely handles large files
   - Send in 2000-character chunks to bypass AppleScript length limits
   - Apply modified text to Overleaf editor in Safari
   - Automatically add BibTeX entries to `mybib.bib`

### LLM Function Calling

CiteAgent uses LLM's Function Calling feature:

**Available Tools:**
- `search_paper(query, limit)`: Search papers
  - Use concise search queries with max 3 words
  - Returns 5 results by default
- `get_bibtex(paper_key)`: Generate BibTeX entry
  - Call **individually** for each paper

LLM calls necessary tools autonomously, ensuring only **real, existing papers** are cited without hallucination.

### Chunk-based File Writing

A special approach is used to overcome AppleScript command length limitations:

1. Split large content into 2000-character chunks
2. `push()` each chunk to JavaScript array
3. Combine all chunks with `join('')`
4. Write combined content to CodeMirror editor

This approach safely handles **files over 5800 characters**.

---

## Troubleshooting

### 1. "Could not connect to Safari" Error

**Cause:** Safari not running or Overleaf not open

**Solution:**
- Verify Safari is running
- Check that Overleaf project is open
- Verify `project_url` in `config.yaml` is correct

### 2. "File 'mybib.bib' not found" Error

**Cause:** No mybib.bib file in Overleaf project

**Solution:**
1. Create a new file in Overleaf project
2. Name it `mybib.bib`
3. Save as empty file
4. Try again

Or if you have a .bib file with a different name:
- Also automatically searches for `references.bib`, `bibliography.bib`, `refs.bib`, etc.

### 3. "Editor not ready" Error

**Cause:** Overleaf editor not fully loaded

**Solution:**
- Refresh page and retry
- Verify `.tex` file is actually open in editor
- Wait a few seconds and try again

### 4. API Key Error

**Cause:** Invalid or unconfigured API key

**Solution:**
- Check API key in `config.yaml`
- Verify no extra spaces or quotes in API key
- Check API key status in Gemini/Upstage console
- For environment variables: `export GEMINI_API_KEY="your-key"`

### 5. No Paper Search Results

**Cause:** Search query too specific or too general

**Solution:**
- Try more general keywords (e.g., "attention mechanism" instead of "transformer")
- Check if papers in that field exist on Semantic Scholar
- Check Semantic Scholar API status

### 6. BibTeX Not Added

**Cause:** Cannot switch to mybib.bib file

**Solution:**
- Manually copy BibTeX entries printed in terminal
- Keep mybib.bib file open in Overleaf and retry
- Verify filename is exactly `mybib.bib`

### 7. "Empty JavaScript result" Error

**Cause:** AppleScript command failed (rare)

**Solution:**
- Restart Safari
- Refresh Overleaf page
- Check terminal accessibility permissions in macOS settings

---

## Advanced Usage

### Managing API Keys with Environment Variables

```bash
# Add to .bashrc or .zshrc
export GEMINI_API_KEY="your_api_key_here"
# or
export UPSTAGE_API_KEY="your_api_key_here"

# Usage
python main.py --interactive
```

### Integration with Python Scripts

```python
from src.citation_agent import CitationAgent
from src.config import Config

# Load configuration
config = Config("config.yaml")
llm_config = config.get_llm_config()

# Initialize agent
if llm_config["provider"] == "gemini":
    agent = CitationAgent(
        provider="gemini",
        api_key=llm_config["api_key"],
        model=llm_config["model"]
    )
else:
    agent = CitationAgent(
        provider="upstage",
        api_key=llm_config["api_key"],
        model=llm_config["model"]
    )

# Process text
text = "Transformers have revolutionized NLP."
modified, bibtex = agent.process_text(text)

print("Modified:", modified)
print("BibTeX:", bibtex)
```

### Using Custom BibTeX Filename

If your project uses a different .bib filename:

1. Open the .bib file in Overleaf in Safari
2. Run the agent with the file open
3. Or rename to one of: `mybib.bib`, `references.bib`, `bibliography.bib`, `refs.bib`

---

## Project Structure

```
citeAgent/
├── main.py                          # Main executable
├── requirements.txt                 # Python dependencies
├── config.yaml                      # Configuration file
├── README.md                        # Documentation (Korean)
├── README_EN.md                     # Documentation (English)
├── test_agent.py                    # Test script
└── src/
    ├── __init__.py
    ├── config.py                    # Configuration management
    ├── paper_search.py              # Semantic Scholar integration
    ├── citation_agent.py            # LLM agent logic
    └── safari_applescript_controller.py  # Safari control
```

---

## Important Notes

- ⚠️ This tool is created for **research assistance purposes**
- ⚠️ Generated citations **must be reviewed and verified**
- ⚠️ Responsibility for inaccurate citations or copyright issues lies with the user
- ⚠️ Overleaf's auto-save feature automatically saves changes - **backup recommended** before important work
- ⚠️ Citations are NOT automatically added to Abstract sections (`\begin{abstract}...\end{abstract}`)

---

## License

MIT License

## References

- [Google Gemini API](https://ai.google.dev/)
- [Upstage API Documentation](https://developers.upstage.ai/)
- [Semantic Scholar API](https://api.semanticscholar.org/)
- [Overleaf](https://www.overleaf.com/)

---

**Made with ❤️ for researchers**
