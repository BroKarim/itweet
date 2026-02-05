"""
Manager for local configuration and persistent storage.
"""
import os
import json
from typing import Optional


class ConfigManager:
    """Handles persistent storage of user configuration like API keys."""

    def __init__(self) -> None:
        # Store in user home: ~/.itweet_config.json
        self.config_path = os.path.expanduser("~/.itweet_config.json")

    def save_api_key(self, api_key: str) -> None:
        """Save the API key to local storage."""
        config = self._load_config()
        config["api_key"] = api_key
        try:
            with open(self.config_path, "w") as f:
                json.dump(config, f)
            print(f"✓ API Key saved locally to {self.config_path}")
        except Exception as exc:
            print(f"⚠️ Warning: Failed to save config: {exc}")

    def get_api_key(self) -> Optional[str]:
        """Retrieve the API key from local storage."""
        config = self._load_config()
        return config.get("api_key")

    def _load_config(self) -> dict:
        """Load configuration from the file."""
        if not os.path.exists(self.config_path):
            return {}
        try:
            with open(self.config_path, "r") as f:
                return json.load(f)
        except Exception:
            return {}
