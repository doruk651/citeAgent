"""Safari automation using AppleScript for macOS."""

import subprocess
import json
import time
from typing import Optional, List


class SafariAppleScriptController:
    """Control Safari using AppleScript to interact with currently open tabs."""

    def __init__(self, overleaf_url: Optional[str] = None):
        """
        Initialize Safari AppleScript controller.

        Args:
            overleaf_url: Optional Overleaf project URL to navigate to
        """
        self.overleaf_url = overleaf_url
        self.connected = False

    def _run_applescript(self, script: str) -> str:
        """
        Execute AppleScript and return output.

        Args:
            script: AppleScript code to execute

        Returns:
            Script output as string
        """
        try:
            result = subprocess.run(
                ['osascript', '-e', script],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode != 0:
                raise Exception(f"AppleScript error: {result.stderr}")

            return result.stdout.strip()

        except subprocess.TimeoutExpired:
            raise Exception("AppleScript execution timed out")
        except Exception as e:
            raise Exception(f"Failed to run AppleScript: {e}")

    def _run_javascript(self, js_code: str) -> str:
        """
        Execute JavaScript in the current Safari tab.

        Args:
            js_code: JavaScript code to execute

        Returns:
            Result as string
        """
        # Remove JavaScript comments to avoid issues when compacting to single line
        import re
        # Remove single-line comments
        js_code = re.sub(r'//.*$', '', js_code, flags=re.MULTILINE)
        # Remove multi-line comments
        js_code = re.sub(r'/\*.*?\*/', '', js_code, flags=re.DOTALL)

        # Escape quotes and newlines
        js_escaped = js_code.replace('\\', '\\\\').replace('"', '\\"').replace('\n', ' ')

        applescript = f'''
        tell application "Safari"
            do JavaScript "{js_escaped}" in current tab of front window
        end tell
        '''

        return self._run_applescript(applescript)

    def connect(self) -> bool:
        """
        Connect to Safari and prepare for automation.

        Returns:
            True if connection successful
        """
        try:
            print("\n[Safari] Connecting to Safari...")

            # Check if Safari is running
            check_script = '''
            tell application "System Events"
                return (name of processes) contains "Safari"
            end tell
            '''

            is_running = self._run_applescript(check_script)

            if is_running != "true":
                print("[Safari] Safari is not running. Starting Safari...")
                self._run_applescript('tell application "Safari" to activate')
                time.sleep(2)

            # Navigate to Overleaf URL if provided
            if self.overleaf_url:
                print(f"\n[Safari] Navigating to: {self.overleaf_url}")

                # Ensure URL opens in editor view
                editor_url = self.overleaf_url
                if '/project/' in editor_url and '#' not in editor_url:
                    # Add editor hash if not present
                    editor_url = editor_url.split('?')[0] + '#editor'

                navigate_script = f'''
                tell application "Safari"
                    activate
                    tell front window
                        if (count of tabs) = 0 then
                            make new tab
                        end if
                        set URL of current tab to "{editor_url}"
                    end tell
                end tell
                '''
                self._run_applescript(navigate_script)
                print("[Safari] Waiting for page to load...")
                time.sleep(8)  # Longer wait for editor to initialize
            else:
                # Just activate Safari to show the current tab
                self._run_applescript('tell application "Safari" to activate')

            # Get current URL
            get_url_script = '''
            tell application "Safari"
                return URL of current tab of front window
            end tell
            '''

            current_url = self._run_applescript(get_url_script)

            # Check if we're on Overleaf
            if "overleaf.com" not in current_url:
                print(f"[Safari] WARNING: Current tab is not on Overleaf")
                print(f"[Safari] Current URL: {current_url}")
                print("[Safari] Please navigate to your Overleaf project in Safari")

                response = input("[Safari] Are you on an Overleaf editor page? (yes/no): ")
                if response.lower() not in ['yes', 'y']:
                    return False

            # Wait for editor to be available (CodeMirror 6 or ACE)
            print("[Safari] Waiting for Overleaf editor to load...")
            editor_ready = False
            for i in range(15):
                try:
                    # Check if CodeMirror 6 or ACE editor is available
                    result = self._run_javascript("""
                        (function() {
                            // Check for CodeMirror 6
                            var elem = window.editor || document.querySelector('.cm-editor');
                            if (elem) {
                                var cmView = elem.CodeMirror || elem.cmView || elem.cm;
                                if (cmView && cmView.view) return 'ready';
                            }
                            // Check for ACE
                            if (typeof ace !== 'undefined') return 'ready';
                            return 'not ready';
                        })();
                    """)
                    if 'ready' in result:
                        editor_ready = True
                        break
                except:
                    pass
                time.sleep(1)

            if not editor_ready:
                print("[Safari] Warning: Editor not detected!")
                print("[Safari] Make sure you're on the Overleaf editor page (not project settings)")

                # Check current URL to give better error message
                try:
                    current_url = self._run_applescript('tell application "Safari" to return URL of current tab of front window')
                    if '/project/' in current_url and 'editor' not in current_url:
                        print("[Safari] Tip: Try clicking a file to open the editor, or add '#editor' to the URL")
                except:
                    pass

            print("[Safari] Successfully connected!")
            print(f"[Safari] Current URL: {current_url}")
            self.connected = True
            return True

        except Exception as e:
            print(f"[Safari] Connection failed: {e}")
            return False

    def get_editor_content(self) -> Optional[str]:
        """
        Get content from Overleaf editor (supports both ACE and CodeMirror 6).

        Returns:
            Editor content as string, or None if failed
        """
        if not self.connected:
            print("[Safari] Not connected!")
            return None

        try:
            print("\n[Safari] Reading editor content...")

            js_code = """
            (function() {
                // Try CodeMirror 6 (new Overleaf)
                var elem = window.editor || document.querySelector('.cm-editor');
                if (elem) {
                    var cmView = elem.CodeMirror || elem.cmView || elem.cm;
                    if (cmView && cmView.view && cmView.view.state && cmView.view.state.doc) {
                        return cmView.view.state.doc.toString();
                    }
                }

                // Fallback to ACE editor (old Overleaf)
                var aceEditor = window.aceEditor || (typeof ace !== 'undefined' && ace.edit('editor'));
                if (aceEditor && aceEditor.getValue) {
                    return aceEditor.getValue();
                }

                return null;
            })();
            """

            content = self._run_javascript(js_code)

            if not content or content == "null":
                print("[Safari] ERROR: Could not find editor!")
                print("[Safari] Make sure you have a file open in the Overleaf editor.")
                return None

            print(f"[Safari] Read {len(content)} characters")
            return content

        except Exception as e:
            print(f"[Safari] Error reading editor: {e}")
            return None

    def set_editor_content(self, content: str, safe_mode: bool = True) -> bool:
        """
        Set content in Overleaf editor (supports both ACE and CodeMirror 6).

        Args:
            content: New content to set
            safe_mode: If True, ask for confirmation before overwriting

        Returns:
            True if successful
        """
        if not self.connected:
            print("[Safari] Not connected!")
            return False

        try:
            if safe_mode:
                print("\n[Safari] WARNING: This will replace ALL editor content!")
                print("[Safari] Make sure you have saved your work or have a backup.")
                response = input("[Safari] Continue? (yes/no): ")
                if response.lower() not in ['yes', 'y']:
                    print("[Safari] Operation cancelled.")
                    return False

            print("\n[Safari] Writing to editor...")
            print(f"[Safari] Content length: {len(content)} characters")

            # Escape content for JavaScript
            content_json = json.dumps(content)
            print(f"[Safari] JSON-encoded content length: {len(content_json)} characters")

            # Split into multiple steps for better debugging
            # Step 1: Store content in a variable
            print("[Safari] Step 1: Storing content...")
            store_js = f"window.__tempContent = {content_json}; 'stored';"
            store_result = self._run_javascript(store_js)
            print(f"[Safari] Store result: '{store_result}'")

            # Step 2: Update editor
            print("[Safari] Step 2: Updating editor...")
            update_js = """
(function() {
    try {
        var content = window.__tempContent;
        if (!content) return 'no_content';

        var elem = window.editor || document.querySelector('.cm-editor');
        if (elem) {
            var cmView = elem.CodeMirror || elem.cmView || elem.cm;
            if (cmView && cmView.view && cmView.view.dispatch) {
                var view = cmView.view;
                var transaction = view.state.update({
                    changes: {from: 0, to: view.state.doc.length, insert: content}
                });
                view.dispatch(transaction);
                delete window.__tempContent;
                return 'cm_success';
            }
        }

        var aceEditor = window.aceEditor || (typeof ace !== 'undefined' && ace.edit('editor'));
        if (aceEditor && aceEditor.setValue) {
            aceEditor.setValue(content, -1);
            delete window.__tempContent;
            return 'ace_success';
        }

        return 'no_editor';
    } catch (e) {
        return 'error: ' + e.message;
    }
})();
"""
            result = self._run_javascript(update_js)
            print(f"[Safari] Update result: '{result}'")

            if 'success' in result:
                print(f"[Safari] Successfully wrote {len(content)} characters")
                return True
            else:
                print("[Safari] ERROR: Could not find editor!")
                print("[Safari] This usually means the editor is not fully loaded yet")
                return False

        except Exception as e:
            print(f"[Safari] Error writing to editor: {e}")
            import traceback
            traceback.print_exc()
            return False

    def get_selected_text(self) -> Optional[str]:
        """
        Get currently selected text in the editor (supports both ACE and CodeMirror 6).

        Returns:
            Selected text or None
        """
        if not self.connected:
            return None

        try:
            js_code = """
            (function() {
                // Try CodeMirror 6 (new Overleaf)
                var elem = window.editor || document.querySelector('.cm-editor');
                if (elem) {
                    var cmView = elem.CodeMirror || elem.cmView || elem.cm;
                    if (cmView && cmView.view && cmView.view.state) {
                        var view = cmView.view;
                        var selection = view.state.selection.main;
                        if (selection.from !== selection.to) {
                            return view.state.doc.sliceString(selection.from, selection.to);
                        }
                    }
                }

                // Fallback to ACE editor (old Overleaf)
                var aceEditor = window.aceEditor || (typeof ace !== 'undefined' && ace.edit('editor'));
                if (aceEditor && aceEditor.getSelectedText) {
                    return aceEditor.getSelectedText();
                }

                return null;
            })();
            """

            selected = self._run_javascript(js_code)

            # AppleScript returns empty string for null/undefined
            if not selected or selected == "null" or selected == "":
                return None

            return selected

        except Exception as e:
            print(f"[Safari] Error getting selection: {e}")
            return None

    def replace_selected_text(self, new_text: str) -> bool:
        """
        Replace currently selected text with new text (supports both ACE and CodeMirror 6).

        Args:
            new_text: Text to insert

        Returns:
            True if successful
        """
        if not self.connected:
            return False

        try:
            new_text_json = json.dumps(new_text)

            js_code = f"""
            (function() {{
                // Try CodeMirror 6 (new Overleaf)
                var elem = window.editor || document.querySelector('.cm-editor');
                if (elem) {{
                    var cmView = elem.CodeMirror || elem.cmView || elem.cm;
                    if (cmView && cmView.view && cmView.view.dispatch) {{
                        var view = cmView.view;
                        var selection = view.state.selection.main;
                        if (selection.from !== selection.to) {{
                            var transaction = view.state.update({{
                                changes: {{from: selection.from, to: selection.to, insert: {new_text_json}}}
                            }});
                            view.dispatch(transaction);
                            return 'success';
                        }}
                        return 'no selection';
                    }}
                }}

                // Fallback to ACE editor (old Overleaf)
                var aceEditor = window.aceEditor || (typeof ace !== 'undefined' && ace.edit('editor'));
                if (aceEditor && aceEditor.session && aceEditor.session.replace) {{
                    aceEditor.session.replace(aceEditor.selection.getRange(), {new_text_json});
                    return 'success';
                }}

                return 'failed';
            }})();
            """

            result = self._run_javascript(js_code)
            return 'success' in result

        except Exception as e:
            print(f"[Safari] Error replacing selection: {e}")
            return False

    def insert_at_cursor(self, text: str) -> bool:
        """
        Insert text at current cursor position.

        Args:
            text: Text to insert

        Returns:
            True if successful
        """
        if not self.connected:
            return False

        try:
            text_json = json.dumps(text)

            js_code = f"""
            (function() {{
                var editor = window.aceEditor || ace.edit('editor');
                if (editor) {{
                    editor.insert({text_json});
                    return 'success';
                }}
                return 'failed';
            }})();
            """

            result = self._run_javascript(js_code)
            return 'success' in result

        except Exception as e:
            print(f"[Safari] Error inserting text: {e}")
            return False

    def switch_to_file(self, filename: str) -> bool:
        """
        Switch to a different file in the project.

        Args:
            filename: Name of file to switch to (e.g., 'main.tex', 'mybib.bib')

        Returns:
            True if successful
        """
        if not self.connected:
            return False

        try:
            print(f"\n[Safari] Switching to file: {filename}")

            js_code = f"""
            (function() {{
                var entities = document.querySelectorAll('.entity-name');
                for (var i = 0; i < entities.length; i++) {{
                    var text = entities[i].textContent.trim();
                    if (text === '{filename}' || text.endsWith('{filename}')) {{
                        entities[i].click();
                        return 'success';
                    }}
                }}

                var fileItems = document.querySelectorAll('.file-tree-item-name');
                for (var i = 0; i < fileItems.length; i++) {{
                    var text = fileItems[i].textContent.trim();
                    if (text === '{filename}' || text.endsWith('{filename}')) {{
                        fileItems[i].click();
                        return 'success';
                    }}
                }}

                return 'failed';
            }})();
            """

            result = self._run_javascript(js_code)

            # Note: JavaScript may return empty string due to AppleScript limits
            # but the click might still have succeeded. Verify by checking editor state.
            if result and 'success' in result:
                print(f"[Safari] Switched to {filename}")
            elif not result or result == '':
                # Empty result - click may have worked, verify by checking editor
                print(f"[Safari] Click returned empty, verifying editor state...")
            else:
                print(f"[Safari] Click result: {result}")

            # Wait for file to load and editor to be ready
            time.sleep(2)  # Increased wait time
            editor_ready = False
            for i in range(10):
                try:
                    check_result = self._run_javascript("""
                        (function() {
                            var elem = window.editor || document.querySelector('.cm-editor');
                            if (elem) {
                                var cmView = elem.CodeMirror || elem.cmView || elem.cm;
                                if (cmView && cmView.view) return 'ready';
                            }
                            if (typeof ace !== 'undefined') return 'ready';
                            return 'not ready';
                        })();
                    """)
                    if check_result and 'ready' in check_result:
                        editor_ready = True
                        print(f"[Safari] Editor ready for {filename}")
                        break
                except:
                    pass
                time.sleep(0.5)

            return editor_ready

        except Exception as e:
            print(f"[Safari] Error switching file: {e}")
            return False

    def append_to_bib_file(self, bibtex_entries: List[str], bib_filename: str = "mybib.bib") -> bool:
        """
        Append BibTeX entries to .bib file.

        Args:
            bibtex_entries: List of BibTeX entry strings
            bib_filename: Name of .bib file (default: mybib.bib)

        Returns:
            True if successful
        """
        if not self.connected or not bibtex_entries:
            return False

        try:
            print(f"\n[Safari] Adding {len(bibtex_entries)} BibTeX entries to {bib_filename}...")

            # Switch to .bib file
            if not self.switch_to_file(bib_filename):
                print(f"[Safari] Could not open {bib_filename}")
                # Try alternative common names
                for alt_name in ["references.bib", "bibliography.bib", "refs.bib"]:
                    if alt_name != bib_filename and self.switch_to_file(alt_name):
                        print(f"[Safari] Using {alt_name} instead")
                        bib_filename = alt_name
                        break
                else:
                    print(f"[Safari] ERROR: No .bib file found!")
                    return False

            # Extra wait for editor to be fully ready after file switch
            print("[Safari] Waiting for editor to be ready...")
            time.sleep(3)  # Increased wait time

            # Verify editor is ready with more attempts
            editor_ready = False
            for attempt in range(10):  # Increased from 5 to 10
                try:
                    test_read = self._run_javascript("""
                        (function() {
                            var elem = window.editor || document.querySelector('.cm-editor');
                            if (elem) {
                                var cmView = elem.CodeMirror || elem.cmView || elem.cm;
                                if (cmView && cmView.view && cmView.view.state && cmView.view.state.doc) {
                                    return 'ready';
                                }
                            }
                            return 'not ready';
                        })();
                    """)
                    if 'ready' in test_read:
                        print(f"[Safari] Editor ready (attempt {attempt + 1})")
                        editor_ready = True
                        break
                except:
                    pass
                print(f"[Safari] Waiting for editor... (attempt {attempt + 1}/10)")
                time.sleep(1.5)  # Increased wait time between attempts

            if not editor_ready:
                print("[Safari] WARNING: Editor may not be fully ready, but proceeding anyway...")

            # Get current content
            current_content = self.get_editor_content()
            if current_content is None:
                print("[Safari] ERROR: Could not read current .bib file content")
                return False

            print(f"[Safari] Current .bib file has {len(current_content)} characters")

            # Append entries one by one to avoid AppleScript string length limits
            print(f"[Safari] Appending {len(bibtex_entries)} entries one by one...")
            success = True

            for i, entry in enumerate(bibtex_entries, 1):
                print(f"[Safari] Adding entry {i}/{len(bibtex_entries)}...")

                # Get latest content for each append
                latest_content = self.get_editor_content()
                if latest_content is None:
                    print(f"[Safari] ERROR: Could not read content before adding entry {i}")
                    success = False
                    break

                # Append this single entry
                new_content = latest_content.rstrip() + "\n\n" + entry + "\n"

                # Use chunked approach to avoid AppleScript string length limits
                # Split content into chunks and build using array join
                chunk_size = 2000  # Safe chunk size for AppleScript (must account for escaping)
                chunks = []
                for j in range(0, len(new_content), chunk_size):
                    chunk = new_content[j:j+chunk_size]
                    chunks.append(chunk)

                # Step 1: Initialize empty array
                init_js = "window.__bibChunks = []; 'initialized';"
                result = self._run_javascript(init_js)
                if result != 'initialized':
                    print(f"[Safari] ERROR: Failed to initialize chunks array")
                    success = False
                    break

                # Step 2: Push each chunk to array
                for chunk_idx, chunk in enumerate(chunks):
                    chunk_json = json.dumps(chunk)
                    # Use push to add to array instead of string concatenation
                    push_js = f"window.__bibChunks.push({chunk_json}); 'chunk_{chunk_idx}';"
                    result = self._run_javascript(push_js)
                    if not result or result != f'chunk_{chunk_idx}':
                        print(f"[Safari] ERROR: Failed to push chunk {chunk_idx}")
                        success = False
                        break

                if not success:
                    break

                # Step 3: Join chunks and update editor
                update_js = """
(function() {
    try {
        var content = window.__bibChunks.join('');
        if (!content) return 'no_content';

        var elem = window.editor || document.querySelector('.cm-editor');
        if (!elem) return 'no_elem';

        var cmView = elem.CodeMirror || elem.cmView || elem.cm;
        if (!cmView || !cmView.view) return 'no_view';

        var view = cmView.view;
        var transaction = view.state.update({
            changes: {from: 0, to: view.state.doc.length, insert: content}
        });
        view.dispatch(transaction);
        delete window.__bibChunks;
        return 'success';
    } catch (e) {
        return 'error: ' + e.message;
    }
})();
"""
                result = self._run_javascript(update_js)

                if 'success' not in result:
                    print(f"[Safari] ERROR: Failed to add entry {i}: {result}")
                    success = False
                    break

                # Small delay between entries
                time.sleep(0.3)

            if success:
                print(f"[Safari] Successfully added {len(bibtex_entries)} entries to {bib_filename}")

                # Switch back to main.tex after updating bib file
                time.sleep(1)
                print("[Safari] Switching back to main.tex...")
                self.switch_to_file("main.tex")
            else:
                print("[Safari] ERROR: Failed to write to .bib file")

            return success

        except Exception as e:
            print(f"[Safari] Error appending to .bib file: {e}")
            import traceback
            traceback.print_exc()
            return False

    def close(self):
        """Disconnect (doesn't close Safari)."""
        if self.connected:
            self.connected = False
            print("[Safari] Disconnected")
