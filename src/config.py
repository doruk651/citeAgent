"""Configuration management for CiteAgent."""

import os
import yaml
from typing import Dict, Any
from pathlib import Path


class Config:
    """Configuration loader and manager."""

    def __init__(self, config_path: str = "config.yaml"):
        """
        Load configuration from file.

        Args:
            config_path: Path to config YAML file
        """
        self.config_path = config_path
        self.config: Dict[str, Any] = {}

        # Try to load config file
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                self.config = yaml.safe_load(f)
        else:
            print(f"[Config] Warning: {config_path} not found, using defaults")

        # Load from environment variables (override file config)
        self._load_from_env()

    def _load_from_env(self):
        """Load configuration from environment variables."""
        # Upstage API key
        if os.getenv("UPSTAGE_API_KEY"):
            if "upstage" not in self.config:
                self.config["upstage"] = {}
            self.config["upstage"]["api_key"] = os.getenv("UPSTAGE_API_KEY")

    def get(self, key_path: str, default: Any = None) -> Any:
        """
        Get configuration value using dot notation.

        Args:
            key_path: Key path like 'upstage.api_key'
            default: Default value if key not found

        Returns:
            Configuration value
        """
        keys = key_path.split('.')
        value = self.config

        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default

        return value

    def get_upstage_api_key(self) -> str:
        """Get Upstage API key."""
        api_key = self.get("upstage.api_key", "")
        if not api_key:
            raise ValueError(
                "Upstage API key not found! "
                "Set it in config.yaml or UPSTAGE_API_KEY environment variable."
            )
        return api_key

    def get_upstage_config(self) -> Dict[str, str]:
        """Get Upstage configuration."""
        return {
            "api_key": self.get_upstage_api_key(),
            "base_url": self.get("upstage.base_url", "https://api.upstage.ai/v1"),
            "model": self.get("upstage.model", "solar-pro2")
        }

    def get_chrome_config(self) -> Dict[str, Any]:
        """Get Chrome debug configuration (deprecated, use get_browser_config)."""
        return {
            "debug_port": self.get("chrome.debug_port", self.get("browser.debug_port", 9222)),
            "user_data_dir": self.get("chrome.user_data_dir", self.get("browser.user_data_dir", "ChromeProfile"))
        }

    def get_browser_config(self) -> Dict[str, Any]:
        """Get browser configuration."""
        # Try new 'browser' config first, fall back to old 'chrome' config
        return {
            "type": self.get("browser.type", "chrome"),
            "debug_port": self.get("browser.debug_port", self.get("chrome.debug_port", 9222)),
            "user_data_dir": self.get("browser.user_data_dir", self.get("chrome.user_data_dir", "ChromeProfile"))
        }

    def get_agent_config(self) -> Dict[str, Any]:
        """Get agent configuration."""
        return {
            "max_papers_per_search": self.get("agent.max_papers_per_search", 5),
            "min_citation_count": self.get("agent.min_citation_count", 10),
            "temperature": self.get("agent.temperature", 0.3)
        }

    def get_semantic_scholar_config(self) -> Dict[str, Any]:
        """Get Semantic Scholar configuration."""
        return {
            "base_url": self.get("semantic_scholar.base_url", "https://api.semanticscholar.org/graph/v1"),
            "api_key": self.get("semantic_scholar.api_key", "")
        }
