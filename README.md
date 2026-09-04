# 🌍 TerraSR
### Multispectral Earth Observation Super-Resolution & AI Analysis Platform

<p align="center">

<b>SIH 2026 • Problem Statement SIH26142</b>

</p>

<p align="center">

From medium-resolution satellite observations to
<br>
<strong>validated, uncertainty-aware, AI-assisted Earth Observation insights.</strong>

</p>

---

## 🚀 Overview

**TerraSR** is an end-to-end Earth Observation platform designed for
**Deep Learning Based Super-Resolution Mapping (SRM) from Medium Resolution Satellite Imagery**.

The core idea is simple:

> Satellite imagery gives us large-area coverage, but many real-world decisions require finer spatial detail.

TerraSR combines:

- 🛰️ **Sentinel-2 multispectral Earth Observation data**
- 🧠 **Transformer-based Super-Resolution using SwinIR architecture**
- 🔬 **Spatial and spectral validation**
- 🎯 **Uncertainty estimation**
- 🌾 **Agricultural analysis**
- 🏙️ **Urban monitoring**
- 🌊 **Disaster assessment**
- 🔄 **Change detection**
- 🤖 **NVIDIA Nemotron-powered AI reasoning and reporting**

into a single workflow.

---

# 💡 The Problem

Medium-resolution satellite imagery is extremely valuable because it provides:

- Wide geographic coverage
- Frequent observations
- Multispectral information
- Long-term temporal monitoring

However, its spatial resolution can become a limitation for fine-scale analysis.

For example, at **10 m spatial resolution**, one pixel represents approximately a:

**10 m × 10 m ground area**

This can make it difficult to distinguish:

- Small buildings
- Narrow roads
- Field boundaries
- Localized flood damage
- Small urban structures
- Fine-scale land-cover changes

Traditional interpolation can make imagery look sharper, but it does not actually learn how real high-resolution structures are formed.

### TerraSR addresses this through learned Super-Resolution.

---

# 🧠 Our Core Idea

Instead of treating Super-Resolution as simple image resizing, TerraSR is designed as a complete Earth Observation pipeline:

```text
                SENTINEL-2
                    │
                    ▼
          ┌───────────────────┐
          │ Scene / AOI       │
          │ Selection         │
          └─────────┬─────────┘
                    │
                    ▼
          ┌───────────────────┐
          │ Quality Control   │
          │ Cloud / Shadow    │
          │ NoData / SCL      │
          └─────────┬─────────┘
                    │
                    ▼
          ┌───────────────────┐
          │ Multispectral     │
          │ Preprocessing     │
          │ B02 B03 B04 B08   │
          └─────────┬─────────┘
                    │
                    ▼
       ┌────────────────────────────┐
       │  Multispectral SwinIR      │
       │  Transformer Super-        │
       │  Resolution Reconstruction │
       └─────────────┬──────────────┘
                     │
                     ▼
          ┌───────────────────┐
          │ Validation        │
          │ PSNR / SSIM       │
          │ RMSE / SAM / ERGAS│
          └─────────┬─────────┘
                    │
                    ▼
          ┌───────────────────┐
          │ Uncertainty       │
          │ Estimation        │
          └─────────┬─────────┘
                    │
                    ▼
      ┌──────────────────────────────┐
      │ Earth Observation Analytics  │
      │                              │
      │ Agriculture                  │
      │ Urban Monitoring             │
      │ Disaster Assessment          │
      │ Change Detection             │
      └──────────────┬───────────────┘
                     │
                     ▼
       ┌────────────────────────────┐
       │ NVIDIA Nemotron             │
       │ AI Reasoning & Orchestration│
       └─────────────┬──────────────┘
                     │
                     ▼
             AI Analyst Report