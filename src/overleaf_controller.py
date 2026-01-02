"""Overleaf browser automation using Selenium."""

import time
import json
import os
from typing import Optional, List, Tuple, Literal
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.safari.options import Options as SafariOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException


class OverleafController:
    """Control Overleaf editor through Selenium."""

    def __init__(self, browser: Literal["chrome", "safari"] = "chrome", debug_port: int = 9222,
                 overleaf_url: Optional[str] = None):
        """
        Initialize Overleaf controller.

        Args:
            browser: Browser to use ("chrome" or "safari")
            debug_port: Chrome remote debugging port (ignored for Safari)
            overleaf_url: Optional direct Overleaf project URL to open
        """
        self.browser = browser.lower()
        self.debug_port = debug_port
        self.overleaf_url = overleaf_url
        self.driver: Optional[webdriver.Remote] = None

    def connect(self) -> bool:
        """
        Connect to browser with Overleaf.

        Returns:
            True if connection successful
        """
        try:
            if self.browser == "safari":
                return self._connect_safari()
            else:
                return self._connect_chrome()

        except Exception as e:
            print(f"[Overleaf] Connection failed: {e}")
            return False

    def _connect_safari(self) -> bool:
        """Connect to Safari browser."""
        print("\n[Overleaf] Connecting to Safari...")

        try:
            # Enable Safari automation first
            print("\n[Overleaf] Enabling Safari Remote Automation...")
            print("[Overleaf] If this is your first time, you may need to:")
            print("[Overleaf]   1. Open Safari → Preferences → Advanced")
            print("[Overleaf]   2. Check 'Show Develop menu in menu bar'")
            print("[Overleaf]   3. Develop → Allow Remote Automation")

            safari_options = SafariOptions()
            self.driver = webdriver.Safari(options=safari_options)

            # Navigate to Overleaf URL if provided
            if self.overleaf_url:
                print(f"\n[Overleaf] Navigating to: {self.overleaf_url}")
                self.driver.get(self.overleaf_url)
                print("[Overleaf] Waiting for page to load...")
                time.sleep(3)  # Wait for page to load

                # Wait for editor to be ready
                print("[Overleaf] Waiting for editor to load...")
                time.sleep(5)  # Give editor time to initialize
            else:
                # Ask user to navigate to Overleaf if not already there
                print("\n[Overleaf] Safari opened. Please navigate to your Overleaf project.")
                input("[Overleaf] Press Enter when you're on the Overleaf editor page...")

            # Verify we're on Overleaf
            current_url = self.driver.current_url
            if "overleaf.com" not in current_url:
                print(f"[Overleaf] WARNING: Current URL doesn't contain 'overleaf.com': {current_url}")
                response = input("[Overleaf] Continue anyway? (yes/no): ")
                if response.lower() not in ['yes', 'y']:
                    return False

            print("[Overleaf] Successfully connected!")
            print(f"[Overleaf] Current URL: {current_url}")
            return True

        except Exception as e:
            print(f"[Overleaf] Safari connection failed: {e}")
            print("\n[Overleaf] Safari setup instructions:")
            print("  1. Open Safari")
            print("  2. Safari → Preferences → Advanced")
            print("  3. Check 'Show Develop menu in menu bar'")
            print("  4. Develop → Allow Remote Automation")
            return False

    def _connect_chrome(self) -> bool:
        """Connect to Chrome browser via remote debugging."""
        print(f"\n[Overleaf] Connecting to Chrome on port {self.debug_port}...")

        try:
            chrome_options = ChromeOptions()
            chrome_options.add_experimental_option(
                "debuggerAddress", f"127.0.0.1:{self.debug_port}"
            )

            self.driver = webdriver.Chrome(options=chrome_options)

            # Navigate to Overleaf URL if provided
            if self.overleaf_url:
                print(f"\n[Overleaf] Navigating to: {self.overleaf_url}")
                self.driver.get(self.overleaf_url)
                print("[Overleaf] Waiting for page to load...")
                time.sleep(3)  # Wait for page to load

                # Wait for editor to be ready
                print("[Overleaf] Waiting for editor to load...")
                time.sleep(5)  # Give editor time to initialize

            # Verify we're on Overleaf
            current_url = self.driver.current_url
            if "overleaf.com" not in current_url:
                if self.overleaf_url:
                    print("[Overleaf] ERROR: Failed to navigate to Overleaf!")
                else:
                    print("[Overleaf] ERROR: Browser is not on Overleaf!")
                print(f"[Overleaf] Current URL: {current_url}")
                print("[Overleaf] Please navigate to your Overleaf project first.")
                return False

            print("[Overleaf] Successfully connected!")
            print(f"[Overleaf] Current URL: {current_url}")
            return True

        except Exception as e:
            print(f"[Overleaf] Chrome connection failed: {e}")
            print("\nMake sure Chrome is running with:")
            print("  Mac: /Applications/Google\\ Chrome.app/Contents/MacOS/Google\\ Chrome "
                  f"--remote-debugging-port={self.debug_port} --user-data-dir=~/ChromeProfile")
            print(f"  Linux: google-chrome --remote-debugging-port={self.debug_port} "
                  "--user-data-dir=~/ChromeProfile")
            print(f"  Windows: chrome.exe --remote-debugging-port={self.debug_port} "
                  "--user-data-dir=C:\\ChromeProfile")
            return False

    def get_editor_content(self) -> Optional[str]:
        """
        Get content from Overleaf ACE editor.

        Returns:
            Editor content as string, or None if failed
        """
        if not self.driver:
            print("[Overleaf] Not connected!")
            return None

        try:
            print("\n[Overleaf] Reading editor content...")

            # Overleaf uses ACE editor
            content = self.driver.execute_script(
                "return window.aceEditor ? window.aceEditor.getValue() : "
                "ace.edit('editor') ? ace.edit('editor').getValue() : null;"
            )

            if content is None:
                print("[Overleaf] ERROR: Could not find ACE editor!")
                print("[Overleaf] Make sure you have a file open in the editor.")
                return None

            print(f"[Overleaf] Read {len(content)} characters")
            return content

        except Exception as e:
            print(f"[Overleaf] Error reading editor: {e}")
            return None

    def set_editor_content(self, content: str, safe_mode: bool = True) -> bool:
        """
        Set content in Overleaf ACE editor.

        Args:
            content: New content to set
            safe_mode: If True, ask for confirmation before overwriting

        Returns:
            True if successful
        """
        if not self.driver:
            print("[Overleaf] Not connected!")
            return False

        try:
            if safe_mode:
                print("\n[Overleaf] WARNING: This will replace ALL editor content!")
                print("[Overleaf] Make sure you have saved your work or have a backup.")
                response = input("[Overleaf] Continue? (yes/no): ")
                if response.lower() not in ['yes', 'y']:
                    print("[Overleaf] Operation cancelled.")
                    return False

            print("\n[Overleaf] Writing to editor...")

            # Escape content for JavaScript
            content_json = json.dumps(content)

            # Set value in ACE editor
            script = f"""
            var editor = window.aceEditor || ace.edit('editor');
            if (editor) {{
                editor.setValue({content_json}, -1);
                return true;
            }}
            return false;
            """

            result = self.driver.execute_script(script)

            if result:
                print(f"[Overleaf] Successfully wrote {len(content)} characters")
                return True
            else:
                print("[Overleaf] ERROR: Could not find ACE editor!")
                return False

        except Exception as e:
            print(f"[Overleaf] Error writing to editor: {e}")
            return False

    def get_selected_text(self) -> Optional[str]:
        """
        Get currently selected text in the editor.

        Returns:
            Selected text or None
        """
        if not self.driver:
            return None

        try:
            selected = self.driver.execute_script(
                "var editor = window.aceEditor || ace.edit('editor'); "
                "return editor ? editor.getSelectedText() : null;"
            )
            return selected

        except Exception as e:
            print(f"[Overleaf] Error getting selection: {e}")
            return None

    def replace_selected_text(self, new_text: str) -> bool:
        """
        Replace currently selected text with new text.

        Args:
            new_text: Text to insert

        Returns:
            True if successful
        """
        if not self.driver:
            return False

        try:
            new_text_json = json.dumps(new_text)

            script = f"""
            var editor = window.aceEditor || ace.edit('editor');
            if (editor) {{
                editor.session.replace(editor.selection.getRange(), {new_text_json});
                return true;
            }}
            return false;
            """

            result = self.driver.execute_script(script)
            return result

        except Exception as e:
            print(f"[Overleaf] Error replacing selection: {e}")
            return False

    def insert_at_cursor(self, text: str) -> bool:
        """
        Insert text at current cursor position.

        Args:
            text: Text to insert

        Returns:
            True if successful
        """
        if not self.driver:
            return False

        try:
            text_json = json.dumps(text)

            script = f"""
            var editor = window.aceEditor || ace.edit('editor');
            if (editor) {{
                editor.insert({text_json});
                return true;
            }}
            return false;
            """

            result = self.driver.execute_script(script)
            return result

        except Exception as e:
            print(f"[Overleaf] Error inserting text: {e}")
            return False

    def get_file_list(self) -> List[str]:
        """
        Get list of files in the project.

        Returns:
            List of file names
        """
        if not self.driver:
            return []

        try:
            # Try to find file tree elements
            # This is fragile and may break with Overleaf UI updates
            files = self.driver.execute_script("""
                var fileItems = document.querySelectorAll('.file-tree-item-name');
                return Array.from(fileItems).map(item => item.textContent.trim());
            """)

            return files if files else []

        except Exception as e:
            print(f"[Overleaf] Error getting file list: {e}")
            return []

    def switch_to_file(self, filename: str) -> bool:
        """
        Switch to a different file in the project.

        Args:
            filename: Name of file to switch to (e.g., 'main.tex', 'references.bib')

        Returns:
            True if successful
        """
        if not self.driver:
            return False

        try:
            print(f"\n[Overleaf] Switching to file: {filename}")

            # Try to click the file in the file tree
            script = f"""
            var fileItems = document.querySelectorAll('.file-tree-item-name');
            for (var i = 0; i < fileItems.length; i++) {{
                if (fileItems[i].textContent.trim() === '{filename}') {{
                    fileItems[i].click();
                    return true;
                }}
            }}
            return false;
            """

            result = self.driver.execute_script(script)

            if result:
                time.sleep(1)  # Wait for file to load
                print(f"[Overleaf] Switched to {filename}")
                return True
            else:
                print(f"[Overleaf] File '{filename}' not found")
                return False

        except Exception as e:
            print(f"[Overleaf] Error switching file: {e}")
            return False

    def append_to_bib_file(self, bibtex_entries: List[str], bib_filename: str = "references.bib") -> bool:
        """
        Append BibTeX entries to .bib file.

        Args:
            bibtex_entries: List of BibTeX entry strings
            bib_filename: Name of .bib file

        Returns:
            True if successful
        """
        if not self.driver or not bibtex_entries:
            return False

        try:
            # Switch to .bib file
            if not self.switch_to_file(bib_filename):
                print(f"[Overleaf] Could not open {bib_filename}")
                return False

            # Get current content
            current_content = self.get_editor_content()
            if current_content is None:
                return False

            # Append new entries
            new_content = current_content.rstrip() + "\n\n" + "\n\n".join(bibtex_entries) + "\n"

            # Set new content
            return self.set_editor_content(new_content, safe_mode=False)

        except Exception as e:
            print(f"[Overleaf] Error appending to .bib file: {e}")
            return False

    def close(self):
        """Close the browser connection (doesn't close the browser)."""
        if self.driver:
            # Note: We don't call driver.quit() because we're connected to an existing browser
            self.driver = None
            print("[Overleaf] Disconnected")
