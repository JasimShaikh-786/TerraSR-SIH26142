"""TerraSR offline-first prototype API with one shared scene manifest."""
from __future__ import annotations
import base64, json, os
from pathlib import Path
from typing import Any
import numpy as np
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter
from pydantic import BaseModel

ROOT=Path(__file__).resolve().parents[1]; DEMO=ROOT/"demo_data"
SCENES:list[dict[str,Any]]=json.loads((DEMO/"scenes.json").read_text(encoding="utf-8")); BY_ID={s["id"]:s for s in SCENES}
app=FastAPI(title="TerraSR Prototype",version="0.3.0")

# ── CORS: read allowed origins from env so both local dev and Vercel prod work
_raw_origins = os.getenv("FRONTEND_ORIGIN","http://localhost:5173")
ALLOWED_ORIGINS = [o.strip().rstrip("/") for o in _raw_origins.split(",") if o.strip()]
if "http://localhost:5173" not in ALLOWED_ORIGINS:
    ALLOWED_ORIGINS.append("http://localhost:5173")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Request(BaseModel): scene_id:str="urban"; prompt:str="Analyze Scene"
def scene(id:str)->dict[str,Any]: return BY_ID.get(id,BY_ID["urban"])
def uri(name:str)->str: return "data:image/png;base64,"+base64.b64encode((DEMO/name).read_bytes()).decode()
def card(id:str)->dict[str,Any]:
 s=scene(id); return {**s,"scene_id":f"S2L2A_DEMO_{s['id'].upper()}_2025","mode":"DEMO DATA","resolution":f"{s['resolution_m']} m","bounds":s["bbox"]}
def ensure(id:str)->None:
 s=scene(id); src=DEMO/s["original_image"]; sr=DEMO/s["sr_preview"]
 if not sr.exists():
  im=Image.open(src).convert("RGB").resize((1800,1800),Image.Resampling.LANCZOS).filter(ImageFilter.UnsharpMask(radius=1.3,percent=115,threshold=4)); ImageEnhance.Contrast(im).enhance(1.06).save(sr)
 uncertainty=DEMO/s["uncertainty_image"]
 if not uncertainty.exists():
  base=Image.open(sr).convert("RGBA").resize((900,900)); lum=np.asarray(base.convert("L"),dtype=np.float32); edge=np.abs(np.gradient(lum,axis=0))+np.abs(np.gradient(lum,axis=1)); alpha=Image.fromarray(((edge>np.percentile(edge,86))*120).astype("uint8"),"L").filter(ImageFilter.GaussianBlur(3)); heat=Image.new("RGBA",base.size,(255,85,55,0)); heat.putalpha(alpha); guide=Image.new("RGBA",base.size,(0,0,0,0)); d=ImageDraw.Draw(guide); d.ellipse((460,290,690,510),fill=(250,179,35,55)); d.ellipse((170,540,380,760),fill=(230,81,56,58)); Image.alpha_composite(Image.alpha_composite(base,guide),heat).save(uncertainty)
def images(id:str)->dict[str,str]:
 ensure(id); s=scene(id); return {"observed":uri(s["original_image"]),"sr_preview":uri(s["sr_preview"]),"uncertainty_image":uri(s["uncertainty_image"])}

# Scene-specific EO analysis — deterministic offline fallback used when Nemotron API unavailable
_SCENE_CONTEXT:dict[str,dict[str,str]] = {
 "urban":{
  "context":"Dense urban environment — Bengaluru Urban Edge, Karnataka, India. Sentinel-2 L2A at 10 m GSD.",
  "obs_quality":"Low cloud cover (4.2%). B02/B03/B04/B08 bands show strong edge contrast for built-up areas. Scene Classification Layer (SCL) confirms clear-sky acquisition.",
  "sr_notes":"Prototype SR preview sharpens road edges and building boundaries via Lanczos upsampling. Fine-scale linear features — narrow roads, building facades — remain model-inferred and require independent validation.",
  "spectral":"B08 (NIR) response is moderate in impervious surfaces. B04 (Red) contrast delineates built-up from vegetated patches. B02–B04 composite supports visual urban interpretation.",
  "uncertainty":"Highest reconstruction uncertainty at sharp boundaries — building edges, narrow roads, and mixed pixels at urban-vegetation transitions. Aleatoric uncertainty is elevated in high-contrast edge regions. Epistemic uncertainty is significant at prototype SR stage.",
  "finding":"SR preview improves visual interpretability of built-up infrastructure patterns. Road delineation confidence is moderate; operational mapping requires reference imagery for geometric validation.",
  "recommendation":"Suitable for coarse urban extent screening and change prioritization. Validate road/building footprints against 1–2 m commercial or drone reference before any mapping product.",
 },
 "agriculture":{
  "context":"Agricultural mosaic — Punjab, India. Smallholder field patterns with varying crop conditions and field boundaries at 10 m.",
  "obs_quality":"Very low cloud cover (2.1%). Clean sun-synchronous acquisition. B04 and B08 provide reliable spectral signal for vegetation analysis. Atmospheric correction (L2A) applied.",
  "sr_notes":"Prototype SR preview enhances field boundary definition and furrow-level texture. NDVI is conceptually derived from B08 and B04; field-scale analysis should remain uncertainty-aware at prototype stage.",
  "spectral":"Strong B08 (NIR) response indicates photosynthetically active vegetation. B04 (Red) absorption consistent with healthy crop canopy. Illustrative NDVI = (B08−B04)/(B08+B04) ≈ 0.63.",
  "uncertainty":"Field boundary pixels carry elevated aleatoric uncertainty from mixed-pixel effects at parcel edges. Epistemic uncertainty is inherent in prototype SR reconstruction and will reduce with trained model inference.",
  "finding":"SR preview supports regional vegetation condition screening and coarse field boundary identification. Individual parcel-level precision is beyond prototype capability.",
  "recommendation":"Use for regional crop-condition prioritization and field-mosaic visualization. Ground-truth parcel boundaries before precision-agriculture decisions or subsidy-mapping workflows.",
 },
 "mixed":{
  "context":"Mixed peri-urban environment — Nashik, Maharashtra, India. Land-cover transitions between built-up, agricultural, and natural areas at 10 m.",
  "obs_quality":"Moderate cloud cover (7.8%). Some spectral uncertainty in cloud-adjacent pixels. SCL mask applied; remaining bands are well-formed and spectrally consistent.",
  "sr_notes":"Prototype SR preview partially resolves edges in transitional zones. Pixel mixtures at land-cover boundaries reduce reconstruction confidence; interpret class boundaries conservatively.",
  "spectral":"B08/B04 ratio supports broad vegetated vs. impervious discrimination. Mixed pixels at urban-rural transitions produce intermediate spectral responses that are ambiguous for supervised classification.",
  "uncertainty":"Transitional pixels exhibit the highest aleatoric uncertainty — compounded by land-cover mixtures and cloud-adjacent spectral distortion. Epistemic uncertainty is uniformly present at prototype stage.",
  "finding":"Conservative land-cover interpretation is appropriate. Dominant cover classes can be screened at coarse resolution; fine boundaries remain uncertain.",
  "recommendation":"Use SR preview for broad land-use mapping and transition-zone identification. Flag edge pixels for higher-resolution validation before change-detection or planning workflows.",
 },
 "disaster":{
  "context":"Flood and change assessment — Assam, India. Inundation boundary mapping and disaster risk screening scenario at 10 m.",
  "obs_quality":"Near-threshold cloud cover (9.5%). Suitable for broad qualitative screening; cloud-adjacent water pixels require careful independent verification.",
  "sr_notes":"Prototype SR preview supports qualitative delineation between inundated and dry land. Water-edge refinement is model-inferred; do not use for precise flood extent mapping without authoritative corroboration.",
  "spectral":"Strong NIR absorption in inundated areas (B08 near-zero over open water). Elevated B04 reflectance in sediment-laden water. Spectral change between pre- and post-event acquisitions is the primary flood indicator.",
  "uncertainty":"Water-land boundaries carry high aleatoric uncertainty due to edge gradients, spectral mixing, and cloud-induced artefacts. Disaster screening must always be corroborated with multi-date, cloud-free observations.",
  "finding":"SR preview enhances visual delineation of potential inundation extent for rapid screening. Quantitative flood-area estimates require validated multi-date multi-sensor analysis.",
  "recommendation":"Use for rapid qualitative prioritization only. Confirm affected-area boundaries with authoritative flood mapping products (e.g. Copernicus EMS rapid mapping) before operational emergency response.",
 },
}

def analyst(s:dict[str,Any],action:str)->str:
 sc=_SCENE_CONTEXT.get(s["id"],_SCENE_CONTEXT["urban"])
 if "validation" in action.lower():
  return (f"**Scene:** {sc['context']}\n\n"
          f"**Spectral Considerations:** {sc['spectral']}\n\n"
          f"**Validation Note:** Displayed PSNR/SSIM/SAM/ERGAS values are DEMO / ILLUSTRATIVE targets from the SR literature. "
          f"Production validation requires co-registered high-resolution reference imagery (e.g. SPOT-6/7 at 1.5 m or equivalent). "
          f"SAM (Spectral Angle Mapper) quantifies spectral-angle preservation across B02/B03/B04/B08. "
          f"ERGAS (Relative Global Dimensional Synthesis Error) measures relative global spectral error across all bands. "
          f"Both metrics are standard for multispectral SR benchmarking (see DSen2, WorldStrat).")
 elif "uncertainty" in action.lower():
  return (f"**Scene:** {sc['context']}\n\n"
          f"**Uncertainty Profile:** {sc['uncertainty']}\n\n"
          f"**Uncertainty Types:**\n"
          f"• Aleatoric: inherent observation noise, mixed pixels, cloud-adjacent spectral distortion — irreducible with more model capacity.\n"
          f"• Epistemic: model-level uncertainty from prototype SR stage — reducible with trained SwinIR inference and ensemble methods.\n\n"
          f"**Production Plan:** Monte Carlo ensemble variance or stochastic test-time dropout for quantified per-pixel confidence intervals.")
 elif "recommend" in action.lower() or "application" in action.lower():
  return (f"**Scene:** {sc['context']}\n\n"
          f"**Key Finding:** {sc['finding']}\n\n"
          f"**Recommended Next Action:** {sc['recommendation']}")
 elif "report" in action.lower():
  return (f"**TerraSR Scene Analysis Summary**\n\n"
          f"**Scene:** {sc['context']}\n\n"
          f"**Observation Quality:** {sc['obs_quality']}\n\n"
          f"**SR Product:** {sc['sr_notes']}\n\n"
          f"**Key Finding:** {sc['finding']}\n\n"
          f"**Recommended Next Action:** {sc['recommendation']}\n\n"
          f"*All SR outputs are PROTOTYPE / DEMO. Independently validate before operational use.*")
 else:
  return (f"**Scene Context:** {sc['context']}\n\n"
          f"**Observation Quality:** {sc['obs_quality']}\n\n"
          f"**SR Product Notes:** {sc['sr_notes']}\n\n"
          f"**Spectral Considerations:** {sc['spectral']}\n\n"
          f"**Uncertainty:** {sc['uncertainty']}\n\n"
          f"**Key Finding:** {sc['finding']}\n\n"
          f"**Recommended Next Action:** {sc['recommendation']}")

@app.get("/api/health")
def health(): return {"status":"ok","brand":"TerraSR","data":"live" if os.getenv("COPERNICUS_CLIENT_ID") else "demo","nemotron":"live" if os.getenv("NVIDIA_API_KEY") else "demo","sr_engine":"prototype","pipeline":"ready"}
@app.post("/api/scenes/search")
def search(_:Request): return {"source":"COPERNICUS — LIVE" if os.getenv("COPERNICUS_CLIENT_ID") else "COPERNICUS — DEMO","notice":"Live credentials configured; demo imagery remains active for this prototype." if os.getenv("COPERNICUS_CLIENT_ID") else "Offline demonstration dataset active. Live metadata is never mixed with demo imagery.","scenes":[card(s["id"]) for s in SCENES]}
@app.post("/api/scenes/select")
def select(q:Request): return {"selected":True,"scene":card(q.scene_id),**images(q.scene_id)}
@app.post("/api/scenes/preview")
def preview(q:Request): return {"metadata":card(q.scene_id),**images(q.scene_id)}
@app.post("/api/preprocess")
def preprocess(q:Request):
 steps=[("Scene quality check","Verify footprint, cloud fraction, viewing angle, and required L2A metadata.","Quality-reviewed scene."),("Cloud / shadow masking","Apply Scene Classification Layer (SCL) to remove cloud, cloud-shadow, and saturated pixels.","Quality-controlled input."),("Band extraction","Read B02 (Blue 490 nm), B03 (Green 560 nm), B04 (Red 665 nm) and B08 (NIR 842 nm).","Four-band multispectral stack."),("Band co-registration","Confirm all four 10 m bands are aligned to the same geographic grid.","Co-registered bands."),("Reflectance normalization","Scale L2A surface reflectance to a consistent model-ready range [0, 1].","Normalized reflectance stack."),("Spatial patch preparation","Prepare overlapping local patches for SR reconstruction inference.","Prototype: 36 patches.")]
 return {"scene":card(q.scene_id),"status":"complete","input":"Sentinel-2 L2A · 10 m · B02/B03/B04/B08","bands":scene(q.scene_id)["bands"],"steps":[{"id":f"{i+1:02}","name":x,"status":"COMPLETE","purpose":y,"output":z} for i,(x,y,z) in enumerate(steps)],"logs":["Loading Sentinel-2 L2A surface reflectance","Validating scene footprint and metadata","Applying SCL cloud/shadow mask","Extracting B02/B03/B04/B08 bands","Co-registering multispectral bands","Normalizing surface reflectance [0,1]","Preparing SR input patches"],**images(q.scene_id)}
@app.post("/api/sr/preview")
def sr(q:Request): return {"scene":card(q.scene_id),"label":"PROTOTYPE SR PREVIEW","method":"Lanczos spatial upsampling with controlled unsharp-mask edge enhancement — lightweight stand-in for trained multispectral SwinIR inference.","target":"Sub-4 m model-reconstructed target","real_swinir":"Current preview uses deterministic image enhancement. Production mode replaces this with trained Multispectral SwinIR (Residual Swin Transformer Blocks; 4-band input tensor [B, 4, H, W]).","baseline_note":"CNN baseline (RCAN — Residual Channel Attention Network, Zhang et al. ECCV 2018) will be evaluated alongside SwinIR using the same dataset, preprocessing, and validation protocol.",**images(q.scene_id)}
@app.post("/api/validation")
def validation(q:Request): return {"scene":card(q.scene_id),"label":"DEMO / ILLUSTRATIVE","note":"Values are illustrative research targets from SR literature — not measured from a co-registered HR reference.","metrics":[{"name":"PSNR","value":"29.8 dB","group":"Spatial fidelity","help":"Peak Signal-to-Noise Ratio. Higher is better. ~28–32 dB is typical for 4× SR benchmarks."},{"name":"SSIM","value":"0.884","group":"Spatial fidelity","help":"Structural Similarity Index: luminance, contrast, and structure. Range [0,1]; closer to 1.0 is better."},{"name":"RMSE","value":"0.041","group":"Spatial fidelity","help":"Root Mean Square Error of normalized surface reflectance. Lower is better."},{"name":"SAM","value":"5.7°","group":"Spectral fidelity","help":"Spectral Angle Mapper: mean spectral-angle difference across all output bands. Lower is better. <6° indicates good spectral preservation."},{"name":"ERGAS","value":"4.12","group":"Spectral fidelity","help":"Relative Global Dimensional Synthesis Error: normalized spectral error across all bands. Lower is better."}],"geospatial":["CRS: EPSG:4326","Projection-consistent output footprint","B02/B03/B04/B08 spectral alignment preserved","SCL cloud mask applied before reconstruction"],"future_criteria":["Hallucination / spectral artefact rate","Semantic consistency with reference HR imagery","Sub-pixel spatial registration error","Application-task performance (NDVI correlation, classification accuracy)"],**images(q.scene_id)}
@app.post("/api/uncertainty")
def uncertainty(q:Request): return {"scene":card(q.scene_id),"label":"PROTOTYPE VISUALIZATION","mean":"DEMO VALUE · 0.18","p95":"DEMO VALUE · 0.47","region":"Elevated uncertainty: sharp boundaries, mixed pixels, and thin linear features","aleatoric":"Inherent observation noise, mixed land-cover pixels, and cloud-adjacent spectral distortion — irreducible with additional model capacity.","epistemic":"Model-level uncertainty from prototype SR stage — reducible with trained SwinIR inference and ensemble methods.","production_plan":"Monte Carlo ensemble variance or stochastic test-time dropout for per-pixel uncertainty confidence intervals.","note":"Uncertainty maps show where reconstruction confidence is lower — not where reconstruction is zero. Fine-scale features are model-inferred.","focus":["sharp boundaries","mixed land cover","thin linear features","building edges","vegetation transitions"],**images(q.scene_id)}
@app.post("/api/agriculture")
def agriculture(q:Request): return {"scene":card(q.scene_id),"label":"DEMO ANALYTICS","ndvi":"DEMO VALUE · 0.63","formula":"NDVI = (B08 − B04) / (B08 + B04)","result":"Vegetation condition screening and field-pattern identification are illustrative outputs. SR-enhanced NDVI requires independent ground-reference validation before agronomic use.","uncertainty":"Field boundaries are model-inferred at prototype stage; parcel-level precision requires trained SR inference and reference delineation.",**images(q.scene_id)}
@app.post("/api/urban")
def urban(q:Request): return {"scene":card(q.scene_id),"label":"DEMO ANALYTICS","result":"SR preview improves visual interpretability of road networks and built-up patterns. Automated feature extraction from prototype SR output is not operationally guaranteed.","uncertainty":"Narrow roads and building edges carry elevated reconstruction uncertainty; validate against 1–2 m reference before mapping.",**images(q.scene_id)}
@app.post("/api/disaster")
def disaster(q:Request): return {"scene":card(q.scene_id),"label":"DEMO ANALYSIS","result":"Pre-event and post-event context supports qualitative flood-extent screening. Water-edge boundaries are model-inferred and should not be used for operational damage assessment.","uncertainty":"Water-land boundaries are high-uncertainty regions. Corroborate with multi-date authoritative flood mapping products.",**images(q.scene_id)}
@app.post("/api/change-detection")
def change(q:Request): return {"scene":card(q.scene_id),"label":"DEMO ANALYSIS","workflow":["Temporal Scene A (pre-event)","Temporal Scene B (post-event)","Radiometric co-normalization","Difference image computation","Change-region identification"],"result":"Potential change areas are illustrative. Multi-temporal co-registration is required for operational change detection.",**images(q.scene_id)}
@app.post("/api/nemotron/analyze")
def nemotron(q:Request):
 s=card(q.scene_id)
 if os.getenv("NVIDIA_API_KEY"):
  try:
   from agent.nemotron import ask_nemotron
   # EO-specific prompt structure for production Nemotron inference
   eo_prompt=(
    f"You are the Earth Observation reasoning layer for TerraSR, an SIH 2026 multispectral super-resolution platform. "
    f"Scene: {s.get('name','')}, {s.get('location','')}. "
    f"Sensor: Sentinel-2 L2A 10 m GSD. Bands used: B02 (Blue 490 nm), B03 (Green 560 nm), B04 (Red 665 nm), B08 (NIR 842 nm). "
    f"Cloud cover: {s.get('cloud_cover','')}%. SR method: Multispectral SwinIR (prototype deterministic preview). "
    f"Task: {q.prompt}. "
    f"Structure your response with these headings: Scene Context, Observation Quality, SR Product Notes, Spectral Considerations, Uncertainty (distinguish aleatoric vs epistemic), Key Finding, Recommended Next Action. "
    f"Be technically grounded and concise. Do not use generic phrases like 'this image looks good'. "
    f"Do not claim SR output is direct observation — it is model-reconstructed."
   )
   return {"scene":s,"mode":"LIVE NEMOTRON","model":"NVIDIA Nemotron 3 Ultra","response":ask_nemotron(eo_prompt)}
  except Exception:
   pass
 return {"scene":s,"mode":"DEMO ANALYST","model":"NVIDIA Nemotron 3 Ultra","response":analyst(s,q.prompt)}
@app.post("/api/report")
def report(q:Request):
 s=card(q.scene_id); sc=_SCENE_CONTEXT.get(q.scene_id,_SCENE_CONTEXT["urban"])
 return {"title":"TerraSR Scene Analysis Report","scene":s,"sections":["Scene","Input","Preprocessing","Super-Resolution","Validation","Uncertainty","Application","AI Analyst"],"markdown":f"# TerraSR Scene Analysis Report\n\n## Scene\n{s['name']} — {s['location']}\nDate: {s.get('date','DEMO')} · Cloud: {s.get('cloud_cover','')}% · {s.get('mode','DEMO DATA')}\n\n## Input\nSentinel-2 L2A · 10 m · B02 (Blue 490 nm) / B03 (Green 560 nm) / B04 (Red 665 nm) / B08 (NIR 842 nm)\n\n## Observation Quality\n{sc['obs_quality']}\n\n## Super-Resolution\nPrototype: deterministic Lanczos upsampling + unsharp-mask edge enhancement.\nProduction target: trained Multispectral SwinIR — 4-band input tensor [B, 4, H, W], Residual Swin Transformer Blocks.\nBaseline: RCAN (Residual Channel Attention Network, Zhang et al. ECCV 2018).\n\n## SR Product Notes\n{sc['sr_notes']}\n\n## Spectral Considerations\n{sc['spectral']}\n\n## Uncertainty\n{sc['uncertainty']}\n\n## Key Finding\n{sc['finding']}\n\n## Recommended Next Action\n{sc['recommendation']}\n\n## Status\nPrototype Demonstration. All SR outputs are model-reconstructed, not directly observed. Production deployment requires trained model inference and independent high-resolution reference validation."}
