"""Configuration regression tests; no credentials or API requests needed."""
import os
import unittest
from unittest.mock import patch

from agent import _llm, model_name


class ConfigTests(unittest.TestCase):
    def test_llm_model_wins_over_legacy_setting(self):
        with patch.dict(os.environ, {
            "LLM_PROVIDER": "groq", "LLM_MODEL": "qwen/qwen3.8-27b",
            "GROQ_MODEL": "openai/gpt-oss-120b", "GROQ_API_KEY": "test-key",
        }, clear=True), patch("agent.ChatGroq") as chat:
            _llm()
            self.assertEqual(chat.call_args.kwargs["model"], "qwen/qwen3.8-27b")
            self.assertEqual(chat.call_args.kwargs["max_tokens"], 900)
            _llm(max_tokens=4000)
            self.assertEqual(chat.call_args.kwargs["max_tokens"], 900)

    def test_legacy_and_default_models(self):
        with patch.dict(os.environ, {"GROQ_MODEL": "legacy-model"}, clear=True):
            self.assertEqual(model_name(), "legacy-model")
        with patch.dict(os.environ, {}, clear=True):
            self.assertEqual(model_name(), "openai/gpt-oss-120b")

    def test_missing_key(self):
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaisesRegex(ValueError, "Set GROQ_API_KEY"):
                _llm()

    def test_unsupported_provider(self):
        with patch.dict(os.environ, {"LLM_PROVIDER": "other"}, clear=True):
            with self.assertRaisesRegex(ValueError, "supports LLM_PROVIDER"):
                model_name()


if __name__ == "__main__":
    unittest.main()
