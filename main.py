#!/usr/bin/env python3
"""
CiteAgent: Automated Citation Assistant for Overleaf

This tool automatically adds citations to your LaTeX documents in Overleaf
by searching for relevant papers and inserting appropriate \\citep{} tags.
"""

import sys
import argparse
from pathlib import Path
from typing import Optional

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.config import Config
from src.citation_agent import CitationAgent
from src.overleaf_controller import OverleafController


def print_banner():
    """Print welcome banner."""
    print("\n" + "="*70)
    print("  CiteAgent - Automated Citation Assistant for Overleaf")
    print("="*70 + "\n")


def run_interactive_mode(config: Config, overleaf_url: Optional[str] = None):
    """
    Run in interactive mode - continuously process selected text.

    Args:
        config: Configuration object
        overleaf_url: Optional Overleaf project URL
    """
    print_banner()
    print("Mode: Interactive")

    if overleaf_url:
        print(f"\nOverleaf URL: {overleaf_url}")

    print("\nInstructions:")
    print("1. Browser will open and navigate to Overleaf")
    print("2. Select text in the editor that needs citations")
    print("3. Press Enter here to process the selection")
    print("4. Type 'quit' to exit\n")

    # Initialize components
    upstage_config = config.get_upstage_config()
    browser_config = config.get_browser_config()
    agent_config = config.get_agent_config()
    semantic_config = config.get_semantic_scholar_config()

    agent = CitationAgent(
        api_key=upstage_config["api_key"],
        base_url=upstage_config["base_url"],
        model=upstage_config["model"],
        temperature=agent_config["temperature"],
        semantic_scholar_api_key=semantic_config["api_key"] if semantic_config["api_key"] else None
    )

    controller = OverleafController(
        browser=browser_config["type"],
        debug_port=browser_config["debug_port"],
        overleaf_url=overleaf_url
    )

    # Connect to Overleaf
    if not controller.connect():
        print("\n[Error] Could not connect to Overleaf!")
        return

    try:
        while True:
            command = input("\n[CiteAgent] Press Enter to process selection (or 'quit'): ").strip()

            if command.lower() in ['quit', 'exit', 'q']:
                print("\n[CiteAgent] Goodbye!")
                break

            # Get selected text
            selected_text = controller.get_selected_text()

            if not selected_text or selected_text.strip() == "":
                print("[CiteAgent] No text selected! Please select text in Overleaf editor.")
                continue

            print(f"\n[CiteAgent] Processing {len(selected_text)} characters...")
            print(f"\n--- Selected Text ---\n{selected_text}\n")

            # Process with agent
            modified_text, bibtex_entries = agent.process_text(selected_text)

            print(f"\n--- Modified Text ---\n{modified_text}\n")

            if bibtex_entries:
                print(f"\n--- BibTeX Entries ({len(bibtex_entries)}) ---")
                for entry in bibtex_entries:
                    print(entry)
                    print()

            # Ask if user wants to apply changes
            response = input("[CiteAgent] Apply changes? (yes/no): ").strip().lower()

            if response in ['yes', 'y']:
                # Replace selected text
                if controller.replace_selected_text(modified_text):
                    print("[CiteAgent] ✓ Text updated in editor")

                    # Add to .bib file
                    if bibtex_entries:
                        if controller.append_to_bib_file(bibtex_entries):
                            print("[CiteAgent] ✓ BibTeX entries added to references.bib")
                        else:
                            print("[CiteAgent] ⚠ Could not update .bib file automatically")
                            print("[CiteAgent] Please add these entries manually to your .bib file")
                else:
                    print("[CiteAgent] ✗ Failed to update text")
            else:
                print("[CiteAgent] Changes discarded")

    except KeyboardInterrupt:
        print("\n\n[CiteAgent] Interrupted by user. Goodbye!")
    finally:
        controller.close()


def run_full_document_mode(config: Config, output_file: str = None, overleaf_url: Optional[str] = None):
    """
    Process the entire document currently open in Overleaf.

    Args:
        config: Configuration object
        output_file: Optional output file path
        overleaf_url: Optional Overleaf project URL
    """
    print_banner()
    print("Mode: Full Document\n")

    if overleaf_url:
        print(f"Overleaf URL: {overleaf_url}\n")

    # Initialize components
    upstage_config = config.get_upstage_config()
    browser_config = config.get_browser_config()
    agent_config = config.get_agent_config()
    semantic_config = config.get_semantic_scholar_config()

    agent = CitationAgent(
        api_key=upstage_config["api_key"],
        base_url=upstage_config["base_url"],
        model=upstage_config["model"],
        temperature=agent_config["temperature"],
        semantic_scholar_api_key=semantic_config["api_key"] if semantic_config["api_key"] else None
    )

    controller = OverleafController(
        browser=browser_config["type"],
        debug_port=browser_config["debug_port"],
        overleaf_url=overleaf_url
    )

    # Connect to Overleaf
    if not controller.connect():
        print("\n[Error] Could not connect to Overleaf!")
        return

    try:
        # Get full document
        content = controller.get_editor_content()
        if not content:
            print("[Error] Could not read editor content!")
            return

        print(f"\n[CiteAgent] Processing document ({len(content)} characters)...")

        # Process with agent
        modified_text, bibtex_entries = agent.process_text(content)

        # Show results
        print(f"\n[CiteAgent] Processing complete!")
        print(f"[CiteAgent] Found {len(bibtex_entries)} papers to cite")

        if output_file:
            # Save to file
            with open(output_file, 'w') as f:
                f.write(modified_text)
            print(f"\n[CiteAgent] Modified text saved to: {output_file}")

            if bibtex_entries:
                bib_file = output_file.replace('.tex', '.bib')
                with open(bib_file, 'w') as f:
                    f.write("\n\n".join(bibtex_entries))
                print(f"[CiteAgent] BibTeX entries saved to: {bib_file}")
        else:
            # Ask if user wants to apply
            print("\n[Warning] This will replace the ENTIRE document!")
            response = input("[CiteAgent] Apply changes to Overleaf? (yes/no): ").strip().lower()

            if response in ['yes', 'y']:
                if controller.set_editor_content(modified_text, safe_mode=True):
                    print("[CiteAgent] ✓ Document updated")

                    if bibtex_entries and controller.append_to_bib_file(bibtex_entries):
                        print("[CiteAgent] ✓ BibTeX entries added")
                else:
                    print("[CiteAgent] ✗ Failed to update document")
            else:
                print("[CiteAgent] Changes not applied")

    finally:
        controller.close()


def run_text_mode(config: Config, input_file: str):
    """
    Process text from a file.

    Args:
        config: Configuration object
        input_file: Path to input .tex file
    """
    print_banner()
    print(f"Mode: File Processing - {input_file}\n")

    # Read input file
    with open(input_file, 'r') as f:
        content = f.read()

    # Initialize agent
    upstage_config = config.get_upstage_config()
    agent_config = config.get_agent_config()

    agent = CitationAgent(
        api_key=upstage_config["api_key"],
        base_url=upstage_config["base_url"],
        model=upstage_config["model"],
        temperature=agent_config["temperature"]
    )

    print(f"[CiteAgent] Processing {len(content)} characters...")

    # Process
    modified_text, bibtex_entries = agent.process_text(content)

    # Output
    output_file = input_file.replace('.tex', '_cited.tex')
    with open(output_file, 'w') as f:
        f.write(modified_text)

    print(f"\n[CiteAgent] Modified text saved to: {output_file}")

    if bibtex_entries:
        bib_file = input_file.replace('.tex', '_cited.bib')
        with open(bib_file, 'w') as f:
            f.write("\n\n".join(bibtex_entries))
        print(f"[CiteAgent] BibTeX entries saved to: {bib_file}")
        print(f"\n[CiteAgent] Found {len(bibtex_entries)} citations")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="CiteAgent - Automated Citation Assistant for Overleaf",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Interactive mode (select text in Overleaf)
  python main.py --interactive

  # With Overleaf URL (auto-navigate)
  python main.py -i -u "https://www.overleaf.com/8375755749spbdsnhhtktg#ecbc6e"

  # Process entire document
  python main.py --full-document

  # With URL
  python main.py -f -u "https://www.overleaf.com/project/xxxxx"

  # Process a .tex file (no browser needed)
  python main.py --file document.tex

  # Save output to file
  python main.py --full-document --output modified.tex
        """
    )

    parser.add_argument(
        '--config', '-c',
        default='config.yaml',
        help='Path to config file (default: config.yaml)'
    )

    parser.add_argument(
        '--interactive', '-i',
        action='store_true',
        help='Run in interactive mode (process selected text)'
    )

    parser.add_argument(
        '--full-document', '-f',
        action='store_true',
        help='Process the entire document currently open in Overleaf'
    )

    parser.add_argument(
        '--file',
        type=str,
        help='Process a .tex file (does not require Overleaf)'
    )

    parser.add_argument(
        '--output', '-o',
        type=str,
        help='Output file path (only for --full-document mode)'
    )

    parser.add_argument(
        '--url', '-u',
        type=str,
        help='Overleaf project URL (e.g., https://www.overleaf.com/project/xxxxx)'
    )

    args = parser.parse_args()

    # Load configuration
    try:
        config = Config(args.config)
    except Exception as e:
        print(f"[Error] Failed to load config: {e}")
        return 1

    # Run appropriate mode
    try:
        if args.file:
            run_text_mode(config, args.file)
        elif args.full_document:
            run_full_document_mode(config, args.output, args.url)
        elif args.interactive:
            run_interactive_mode(config, args.url)
        else:
            # Default to interactive mode
            print("No mode specified, using interactive mode.")
            print("Use --help to see all options.\n")
            run_interactive_mode(config, args.url)

        return 0

    except KeyboardInterrupt:
        print("\n\n[CiteAgent] Interrupted by user.")
        return 130
    except Exception as e:
        print(f"\n[Error] {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
