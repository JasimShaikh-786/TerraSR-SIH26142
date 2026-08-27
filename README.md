# TerraSR — Offline-first Earth Observation Super-Resolution Prototype

A local, judge-ready multispectral Earth Observation Super-Resolution Platform. It preserves the project's existing `agent/nemotron.py`, `preprocessing/`, `dataset/metadata.py`, and `models/swinir/` materials while adding a FastAPI demonstration backend and React/Vite frontend.

## Run locally

```bat
setup.bat
run.bat
```

Open http://localhost:5173. Stop services with `stop.bat`.

## Offline behavior

The application bundles deterministic Bengaluru Urban Edge, Punjab Agricultural Mosaic, Nashik Mixed Peri-Urban, and Assam Flood / Change Assessment scenarios. `demo_data/scenes.json` is the single source of scene metadata and asset paths; every stage uses the same selected scene. No Internet, Copernicus credentials, or NVIDIA API key is required for a complete judge walkthrough.

## Optional live configuration

Copy `.env.example` to `.env` and fill optional `COPERNICUS_CLIENT_ID`, `COPERNICUS_CLIENT_SECRET`, `COPERNICUS_INSTANCE_ID`, and `NVIDIA_API_KEY`. Secrets stay backend-only. Production Copernicus search and trained SwinIR execution are deliberately future work.

## Accuracy statement

`PROTOTYPE SR PREVIEW` uses deterministic Lanczos upscaling, controlled sharpening and contrast enhancement. It does **not** run trained SwinIR weights and represents a *sub-4m model-reconstructed target* — never true 2.5m observed satellite imagery. Validation and application results are marked `DEMO / ILLUSTRATIVE`; uncertainty is `PROTOTYPE UNCERTAINTY`.

Use the global **JUDGE MODE** control for a ~48-second guided presentation. See [docs/JUDGE_DEMO.md](docs/JUDGE_DEMO.md) for the presentation flow.
