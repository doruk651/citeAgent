#!/usr/bin/env python3
"""
Setup verification script for CiteAgent.
Checks if all dependencies and configurations are correct.
"""

import sys
import os
from pathlib import Path

def print_header(text):
    """Print a formatted header."""
    print("\n" + "="*70)
    print(f"  {text}")
    print("="*70 + "\n")

def print_status(check_name, passed, message=""):
    """Print check status."""
    status = "✓" if passed else "✗"
    color = "\033[92m" if passed else "\033[91m"
    reset = "\033[0m"
    print(f"{color}{status}{reset} {check_name}")
    if message:
        print(f"  → {message}")

def check_python_version():
    """Check Python version."""
    version = sys.version_info
    passed = version.major == 3 and version.minor >= 8
    print_status(
        "Python Version (>=3.8)",
        passed,
        f"Found: {version.major}.{version.minor}.{version.micro}"
    )
    return passed

def check_dependencies():
    """Check if all required packages are installed."""
    required = [
        "openai",
        "selenium",
        "webdriver_manager",
        "requests",
        "yaml",
        "bibtexparser"
    ]

    missing = []
    for package in required:
        try:
            if package == "yaml":
                __import__("yaml")
            elif package == "webdriver_manager":
                __import__("webdriver_manager")
            else:
                __import__(package)
        except ImportError:
            missing.append(package)

    passed = len(missing) == 0
    message = "All packages installed" if passed else f"Missing: {', '.join(missing)}"
    print_status("Python Dependencies", passed, message)

    if not passed:
        print("  → Fix: pip install -r requirements.txt")

    return passed

def check_config_file():
    """Check if config file exists and is valid."""
    config_path = "config.yaml"

    if not os.path.exists(config_path):
        print_status("Configuration File", False, f"{config_path} not found")
        print("  → Fix: cp config.yaml.example config.yaml")
        return False

    try:
        import yaml
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)

        # Check for API key
        api_key = config.get("upstage", {}).get("api_key", "")

        if not api_key or api_key == "your_upstage_api_key_here":
            print_status("Upstage API Key", False, "API key not configured")
            print("  → Fix: Edit config.yaml and add your Upstage API key")
            print("  → Get key from: https://console.upstage.ai/")
            return False

        print_status("Configuration File", True, "Valid config with API key")
        return True

    except Exception as e:
        print_status("Configuration File", False, f"Error: {e}")
        return False

def check_chrome():
    """Check if Chrome is available."""
    chrome_paths = [
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",  # Mac
        "/usr/bin/google-chrome",  # Linux
        "/usr/bin/chromium",  # Linux (Chromium)
        "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",  # Windows
        "C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe"  # Windows
    ]

    chrome_found = any(os.path.exists(path) for path in chrome_paths)

    # Also check if it's in PATH
    if not chrome_found:
        import shutil
        chrome_found = shutil.which("google-chrome") is not None or \
                      shutil.which("chromium") is not None

    print_status("Google Chrome", chrome_found,
                "Chrome found" if chrome_found else "Chrome not found in standard locations")

    if not chrome_found:
        print("  → Install Chrome from: https://www.google.com/chrome/")

    return chrome_found

def check_chromedriver():
    """Check if ChromeDriver is available."""
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.service import Service
        from webdriver_manager.chrome import ChromeDriverManager

        # Try to get chromedriver
        driver_path = ChromeDriverManager().install()
        passed = driver_path is not None

        print_status("ChromeDriver", passed, "Available via webdriver-manager")
        return passed

    except Exception as e:
        print_status("ChromeDriver", False, f"Error: {e}")
        return False

def test_semantic_scholar():
    """Test connection to Semantic Scholar API."""
    try:
        import requests
        response = requests.get(
            "https://api.semanticscholar.org/graph/v1/paper/search",
            params={"query": "test", "limit": 1},
            timeout=5
        )
        passed = response.status_code == 200

        print_status("Semantic Scholar API", passed,
                    "API accessible" if passed else f"HTTP {response.status_code}")
        return passed

    except Exception as e:
        print_status("Semantic Scholar API", False, f"Connection error: {e}")
        return False

def test_upstage_api():
    """Test Upstage API connection."""
    try:
        sys.path.insert(0, str(Path(__file__).parent / "src"))
        from src.config import Config

        config = Config("config.yaml")
        api_key = config.get_upstage_api_key()

        from openai import OpenAI
        client = OpenAI(
            api_key=api_key,
            base_url="https://api.upstage.ai/v1"
        )

        # Simple test call
        response = client.chat.completions.create(
            model="solar-pro2",
            messages=[{"role": "user", "content": "Hi"}],
            max_tokens=10
        )

        passed = response is not None
        print_status("Upstage API", passed, "API key valid and working")
        return passed

    except ValueError as e:
        print_status("Upstage API", False, str(e))
        return False
    except Exception as e:
        print_status("Upstage API", False, f"API error: {e}")
        print("  → Check your API key in config.yaml")
        return False

def main():
    """Run all verification checks."""
    print_header("CiteAgent Setup Verification")

    print("Checking system requirements...\n")

    checks = [
        ("Python Version", check_python_version),
        ("Dependencies", check_dependencies),
        ("Configuration", check_config_file),
        ("Chrome Browser", check_chrome),
        ("ChromeDriver", check_chromedriver),
        ("Semantic Scholar", test_semantic_scholar),
        ("Upstage API", test_upstage_api)
    ]

    results = {}
    for name, check_func in checks:
        try:
            results[name] = check_func()
        except Exception as e:
            print_status(name, False, f"Unexpected error: {e}")
            results[name] = False
        print()

    # Summary
    print_header("Summary")

    passed_count = sum(1 for v in results.values() if v)
    total_count = len(results)

    print(f"Passed: {passed_count}/{total_count} checks\n")

    if passed_count == total_count:
        print("✓ All checks passed! CiteAgent is ready to use.")
        print("\nNext steps:")
        print("  1. Start Chrome: ./start_chrome.sh")
        print("  2. Open Overleaf in Chrome")
        print("  3. Run: python main.py --interactive")
        print("\nOr test without Overleaf:")
        print("  python test_agent.py --test all")
        return 0
    else:
        print("✗ Some checks failed. Please fix the issues above.")
        print("\nQuick fixes:")
        print("  - Dependencies: pip install -r requirements.txt")
        print("  - Config: cp config.yaml.example config.yaml")
        print("  - API key: Edit config.yaml")
        return 1

if __name__ == "__main__":
    sys.exit(main())
