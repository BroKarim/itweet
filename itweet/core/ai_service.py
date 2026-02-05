"""
Service for AI-driven selection and tweet generation using OpenRouter.
"""
import os
import json
from typing import Optional
import urllib.request
import urllib.error

from .config_manager import ConfigManager


class AIServiceError(Exception):
    """Exception raised when AI service fails."""


class AIService:
    """Handles AI calls via OpenRouter."""

    def __init__(self, api_key: Optional[str] = None, model: str = "google/gemini-2.5-flash"):
        """
        Initialize AIService.

        Args:
            api_key: OpenRouter API key. If None, tries env or local config.
            model: OpenRouter model name.
        """
        self.config_manager = ConfigManager()
        self.api_key = api_key or self._get_api_key_from_env() or self.config_manager.get_api_key()
        self.model = model
        self.api_url = "https://openrouter.ai/api/v1/chat/completions"

    def _get_api_key_from_env(self) -> Optional[str]:
        env_vars = [
            "OPENROUTER_API_KEY",
            "ITWEET_API_KEY",
            "AI_API_KEY",
        ]
        for var in env_vars:
            key = os.getenv(var)
            if key:
                return key
        return None

    def validate_api_key(self) -> bool:
        return self.api_key is not None and len(self.api_key) > 0

    def generate_text(self, prompt: str) -> str:
        """
        Generate text using OpenRouter.

        Args:
            prompt: The prompt to send.

        Returns:
            Response content.
        """
        if not self.validate_api_key():
            raise AIServiceError(
                "No API key found. Please set OPENROUTER_API_KEY environment variable "
                "or provide it via CLI when implemented."
            )

        return self._call_openrouter_api(prompt)

    def _call_openrouter_api(self, prompt: str) -> str:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/yourusername/itweet",
            "X-Title": "iTweet",
        }

        data = {
            "model": self.model,
            "messages": [
                {"role": "user", "content": prompt},
            ],
        }

        try:
            req = urllib.request.Request(
                self.api_url,
                data=json.dumps(data).encode("utf-8"),
                headers=headers,
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=60) as response:
                result = json.loads(response.read().decode("utf-8"))

            if "choices" in result and result["choices"]:
                content = result["choices"][0]["message"]["content"]
                return content.strip()
            raise AIServiceError("Unexpected API response format")
        except urllib.error.HTTPError as exc:
            error_body = exc.read().decode("utf-8")
            raise AIServiceError(f"API request failed (HTTP {exc.code}): {error_body}") from exc
        except urllib.error.URLError as exc:
            raise AIServiceError(f"Network error: {str(exc)}") from exc
        except json.JSONDecodeError as exc:
            raise AIServiceError(f"Failed to parse API response: {str(exc)}") from exc
