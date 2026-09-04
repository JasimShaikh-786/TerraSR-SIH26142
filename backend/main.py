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
app=FastAPI(title="TerraSR Prototype",version="0.2.0")

# ── CORS: read allowed origins from env so both local dev and Vercel prod work
_raw_origins = os.getenv("FRONTEND_ORIGIN","http://localhost:5173")
ALLOWED_ORIGINS = [o.strip().rstrip("/") for o in _raw_origins.split(",") if o.strip()]
# Always include localhost for dev
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
def analyst(s:dict[str,Any],action:str)->str:
 cores={"urban":"The selected urban-focused demonstration supports cautious road and built-up interpretation. Boundary regions carry higher reconstruction uncertainty and need independent reference validation.","agriculture":"The selected agricultural demonstration supports vegetation-focused interpretation. NDVI is conceptually derived from B08 and B04; reconstructed field boundaries remain model-inferred.","mixed":"The selected mixed peri-urban demonstration supports conservative interpretation of land-cover transitions, where pixel mixtures have elevated uncertainty.","disaster":"The selected flood/change demonstration supports qualitative pre/post screening. Water and mixed-land-cover boundaries deserve heightened uncertainty review."}
 suffix=" Review quality control before using the prototype SR preview as a model-reconstructed aid."
 if "validation" in action.lower(): suffix=" Current values are DEMO / ILLUSTRATIVE and do not represent a measured production benchmark."
 elif "uncertainty" in action.lower(): suffix=" Fine-scale features are model-inferred and should be independently validated before operational use."
 elif "recommend" in action.lower(): suffix=" Recommended use: screening and prioritization, followed by authoritative-data review."
 elif "report" in action.lower(): suffix=" A TerraSR report summarizes input, reconstruction, validation, uncertainty and application context."
 return cores[s["id"]]+suffix

@app.get("/api/health")
def health(): return {"status":"ok","brand":"TerraSR","data":"live" if os.getenv("COPERNICUS_CLIENT_ID") else "demo","nemotron":"live" if os.getenv("NVIDIA_API_KEY") else "demo","sr_engine":"prototype","pipeline":"ready"}
@app.post("/api/scenes/search")
def search(_:Request): return {"source":"COPERNICUS — LIVE" if os.getenv("COPERNICUS_CLIENT_ID") else "COPERNICUS — DEMO","notice":"Live credentials configured; demo imagery remains active for this prototype." if os.getenv("COPERNICUS_CLIENT_ID") else "Offline demonstration dataset active.","scenes":[card(s["id"]) for s in SCENES]}
@app.post("/api/scenes/select")
def select(q:Request): return {"selected":True,"scene":card(q.scene_id),**images(q.scene_id)}
@app.post("/api/scenes/preview")
def preview(q:Request): return {"metadata":card(q.scene_id),**images(q.scene_id)}
@app.post("/api/preprocess")
def preprocess(q:Request):
 steps=[("Scene quality check","Confirm footprint, cloud conditions and required metadata.","Quality-reviewed scene."),("Cloud / shadow masking","Remove pixels affected by clouds or shadows.","Quality-controlled input."),("Band extraction","Read B02, B03, B04 and B08 multispectral signal.","Four-band input stack."),("Band alignment","Ensure every band represents the same geographic pixels.","Co-registered bands."),("Reflectance normalization","Scale source signal into a consistent model-ready range.","Normalized reflectance."),("Spatial patch preparation","Prepare consistent local patches for reconstruction.","36 prototype patches.")]
 return {"scene":card(q.scene_id),"status":"complete","input":"Sentinel-2 L2A · 10 m","bands":scene(q.scene_id)["bands"],"steps":[{"id":f"{i+1:02}","name":x,"status":"COMPLETE","purpose":y,"output":z} for i,(x,y,z) in enumerate(steps)],"logs":["Loading Sentinel-2 L2A","Validating footprint","Extracting B02/B03/B04/B08","Applying quality mask","Aligning bands","Normalizing reflectance","Preparing SR patches"],**images(q.scene_id)}
@app.post("/api/sr/preview")
def sr(q:Request): return {"scene":card(q.scene_id),"label":"PROTOTYPE SR PREVIEW","method":"High-quality Lanczos upsampling, controlled sharpening, edge enhancement and local contrast enhancement.","target":"Sub-4 m model-reconstructed target","real_swinir":"Current preview uses deterministic image enhancement. Production mode will replace this step with trained multispectral SwinIR inference.",**images(q.scene_id)}
@app.post("/api/validation")
def validation(q:Request): return {"scene":card(q.scene_id),"label":"DEMO / ILLUSTRATIVE","metrics":[{"name":"PSNR","value":"29.8 dB","group":"Spatial fidelity","help":"Measures reconstruction error using signal-to-noise ratio."},{"name":"SSIM","value":"0.884","group":"Spatial fidelity","help":"Measures structural similarity."},{"name":"RMSE","value":"0.041","group":"Spatial fidelity","help":"Measures average reconstruction error."},{"name":"SAM","value":"5.7°","group":"Spectral fidelity","help":"Measures spectral-angle difference."},{"name":"ERGAS","value":"4.12","group":"Spectral fidelity","help":"Measures relative global spectral error."}],"geospatial":["CRS: EPSG:4326","Footprint: consistent demo scene","Band alignment: complete"],**images(q.scene_id)}
@app.post("/api/uncertainty")
def uncertainty(q:Request): return {"scene":card(q.scene_id),"label":"PROTOTYPE VISUALIZATION","mean":"DEMO VALUE · 0.18","p95":"DEMO VALUE · 0.47","region":"High uncertainty: sharp boundaries and mixed pixels","note":"Fine-scale features are model-inferred and should be independently validated before operational use.","focus":["sharp boundaries","mixed land cover","thin linear features","building edges","vegetation transitions"],**images(q.scene_id)}
@app.post("/api/agriculture")
def agriculture(q:Request): return {"scene":card(q.scene_id),"label":"DEMO ANALYTICS","ndvi":"DEMO VALUE · 0.63","formula":"(B08 − B04) / (B08 + B04)","result":"Vegetation condition, potential stress and field interpretation are illustrative screening outputs.","uncertainty":"Field boundaries remain model-inferred.",**images(q.scene_id)}
@app.post("/api/urban")
def urban(q:Request): return {"scene":card(q.scene_id),"label":"DEMO ANALYTICS","result":"Improved visual interpretability for building/road context and edge review; not guaranteed feature extraction.","uncertainty":"Thin linear features and boundaries require independent validation.",**images(q.scene_id)}
@app.post("/api/disaster")
def disaster(q:Request): return {"scene":card(q.scene_id),"label":"DEMO ANALYSIS","result":"Pre-event and post-event context supports qualitative change screening.","uncertainty":"Water boundaries and mixed cover are higher-uncertainty regions.",**images(q.scene_id)}
@app.post("/api/change-detection")
def change(q:Request): return {"scene":card(q.scene_id),"label":"DEMO ANALYSIS","workflow":["Scene A","Scene B","Co-registration","Difference map"],"result":"Potential change areas are illustrative; no operational affected-area claim is made.",**images(q.scene_id)}
@app.post("/api/nemotron/analyze")
def nemotron(q:Request):
 s=card(q.scene_id)
 if os.getenv("NVIDIA_API_KEY"):
  try:
   from agent.nemotron import ask_nemotron
   return {"scene":s,"mode":"LIVE NEMOTRON","model":"NVIDIA Nemotron 3 Ultra","response":ask_nemotron(q.prompt)}
  except Exception:
   pass
 return {"scene":s,"mode":"DEMO ANALYST","model":"NVIDIA Nemotron 3 Ultra","response":analyst(s,q.prompt)}
@app.post("/api/report")
def report(q:Request):
 s=card(q.scene_id); return {"title":"TerraSR Scene Analysis Report","scene":s,"sections":["Scene","Input","Preprocessing","Super-Resolution","Validation","Uncertainty","Application","AI Analyst"],"markdown":f"# TerraSR Scene Analysis Report\n\n## Scene\n{s['name']} — {s['location']} ({s['mode']})\n\n## Input\n10 m Sentinel-2 L2A · B02/B03/B04/B08\n\n## Super-Resolution\nSub-4 m model-reconstructed target via a PROTOTYPE SR PREVIEW.\n\n## Status\nPrototype Demonstration. Production deployment requires trained model inference and independent high-resolution validation."}
