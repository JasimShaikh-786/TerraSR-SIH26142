from nemotron import ask_nemotron


def main() -> None:
    prompt = """
We are building SIH26142:

Deep Learning Based Super Resolution Mapping
from Medium Resolution Satellite Imagery.

Input:
Sentinel-2 L2A, approximately 10 m resolution.

Planned model:
Multispectral SwinIR.

Target:
Sub-4-meter reconstructed output.

Explain in 5 concise points what an AI orchestration
agent should do in this system. Do not invent measurements.
"""

    answer = ask_nemotron(prompt)

    print("\n===== NEMOTRON =====\n")
    print(answer)


if __name__ == "__main__":
    main()