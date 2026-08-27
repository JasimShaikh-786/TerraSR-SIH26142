"""Safe adapter for the existing agent/nemotron.py integration.

This import is deliberately lazy because the existing module correctly refuses
to start without NVIDIA_API_KEY; the judge prototype must remain offline-safe.
"""
import os

def analyze(prompt: str) -> tuple[str, str]:
    if os.getenv("NVIDIA_API_KEY"):
        try:
            from agent.nemotron import ask_nemotron
            return "LIVE NEMOTRON", ask_nemotron(prompt)
        except Exception:
            pass
    return "DEMO ANALYST", "Offline deterministic analyst response: validate inferred fine-scale detail independently."
