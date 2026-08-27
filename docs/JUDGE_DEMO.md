# Judge demo runbook

1. Run `setup.bat` once and then `run.bat`.
2. Open http://localhost:5173 and select any bundled scene.
3. Click the global **JUDGE MODE** button. The guided timeline visits Acquire, Quality, Preprocess, Reconstruct, Validate, Uncertainty, Analyze and Explain in about 48 seconds.
4. In SR Engine, move the slider to compare 10 m observed input with the clearly labelled PROTOTYPE SR PREVIEW.
5. SwinIR describes the future four-band model path; this build never asserts trained SwinIR inference.
6. AI Analyst returns a deterministic offline DEMO ANALYST response without an NVIDIA key.

All validation statistics and application outputs are DEMO / ILLUSTRATIVE. The target is a **sub-4m model-reconstructed target**, not true 2.5m observed satellite imagery. Fine-scale content is model-inferred and should be independently validated.
