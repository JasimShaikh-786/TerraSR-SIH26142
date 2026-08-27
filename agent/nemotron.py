import os
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

PROJECT_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(PROJECT_ROOT / ".env")

api_key = os.getenv("NVIDIA_API_KEY")

if not api_key:
    raise RuntimeError(
        "NVIDIA_API_KEY is missing. Put it in C:\\SIH26142-SRM\\.env"
    )

client = OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key=api_key,
)

MODEL = "nvidia/nemotron-3-ultra-550b-a55b"


def ask_nemotron(prompt: str) -> str:
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are the reasoning and orchestration layer "
                    "for an Earth Observation Super-Resolution Mapping "
                    "system using Sentinel-2 and SwinIR."
                ),
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
        temperature=0.2,
        top_p=0.95,
        max_tokens=4096,
    )

    return response.choices[0].message.content or ""