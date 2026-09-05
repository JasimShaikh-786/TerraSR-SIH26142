import React, { useEffect, useState } from 'react';
import { createRoot } from 'react-dom/client';
import './styles.css';

// ─── Types ───────────────────────────────────────────────────────────────────
type Any = Record<string, any>;
type Page =
  | 'Dashboard'
  | 'Acquire'
  | 'Preprocess'
  | 'SR Engine'
  | 'Validate'
  | 'Uncertainty'
  | 'Analysis'
  | 'AI Analyst'
  | 'Architecture'
  | 'Report'
  | 'About';

// ─── API helper ──────────────────────────────────────────────────────────────
// In dev: VITE_API_BASE_URL is empty → Vite proxy routes /api → localhost:8000
// In prod: VITE_API_BASE_URL is the Railway URL → calls go directly to Railway
const API_BASE = (import.meta.env.VITE_API_BASE_URL ?? '').replace(/\/$/, '');

const api = async (path: string, body: Any = {}): Promise<Any> => {
  const isGet = path === '/health';
  const url = API_BASE ? `${API_BASE}/api${path}` : `/api${path}`;
  const r = await fetch(url, {
    method: isGet ? 'GET' : 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: isGet ? undefined : JSON.stringify(body),
  });
  if (!r.ok) throw new Error('API unavailable');
  return r.json();
};


// ─── Constants ───────────────────────────────────────────────────────────────
const NAV_PAGES: Page[] = [
  'Dashboard', 'Acquire', 'Preprocess', 'SR Engine',
  'Validate', 'Uncertainty', 'Analysis', 'AI Analyst', 'Architecture',
];

const SCENE_NAMES: Record<string, string> = {
  urban:       'Bengaluru Urban Edge',
  agriculture: 'Punjab Agricultural Mosaic',
  mixed:       'Nashik Mixed Peri-Urban',
  disaster:    'Assam Flood / Change Assessment',
};

const CLOUD_COVER: Record<string, number> = {
  urban: 4.2, agriculture: 2.1, mixed: 7.8, disaster: 9.5,
};

// Judge Mode workflow steps
const WORKFLOW: [Page, string, string, string][] = [
  ['Acquire',    'Acquire',     'Select one consistent Sentinel-2 L2A demonstration scene.',         'A known scene anchors every stage of the story.'],
  ['Preprocess', 'Quality',     'Review scene quality and cloud/shadow conditions.',                   'Input quality constrains responsible interpretation.'],
  ['Preprocess', 'Preprocess',  'Extract, align and normalize B02/B03/B04/B08.',                       'The model needs consistent multispectral pixels.'],
  ['SR Engine',  'Reconstruct', 'Create a source-derived prototype SR preview.',                       'Fine-scale detail is model-reconstructed, not directly observed.'],
  ['Validate',   'Validate',    'Review spatial, spectral and geospatial checks.',                     'Scientific validation frames usefulness.'],
  ['Uncertainty','Uncertainty', 'Visualize where reconstruction is less reliable.',                    'Not every fine-scale feature is equally certain.'],
  ['Analysis',   'Analyze',     'Apply the selected scene to EO interpretation.',                      'Downstream use remains uncertainty-aware.'],
  ['AI Analyst', 'Explain',     'Nemotron summarizes the current scene context.',                      'Reasoning is separate from image reconstruction.'],
];

// Route mapping: page → API endpoint
const PAGE_ROUTE: Record<string, string> = {
  Dashboard:    '/scenes/preview',
  Acquire:      '/scenes/search',
  Preprocess:   '/preprocess',
  'SR Engine':  '/sr/preview',
  Validate:     '/validation',
  Uncertainty:  '/uncertainty',
  Analysis:     '/agriculture',
  'AI Analyst': '/nemotron/analyze',
  Report:       '/report',
};

// ─── Primitive Components ─────────────────────────────────────────────────────
function Chip({ children }: { children: React.ReactNode }) {
  return <span className="chip">{children}</span>;
}

function Badge({ children }: { children: React.ReactNode }) {
  return <span className="badge">{children}</span>;
}

function DemoBadge({ children = 'DEMO / ILLUSTRATIVE' }: { children?: React.ReactNode }) {
  return <span className="badge demo-badge">{children}</span>;
}

function Panel({ children, className = '' }: { children: React.ReactNode; className?: string }) {
  return <section className={'panel ' + className}>{children}</section>;
}

function Head({ eyebrow, title, subtitle }: { eyebrow: string; title: string; subtitle: string }) {
  return (
    <section className="head">
      <span>{eyebrow}</span>
      <h1>{title}</h1>
      <p>{subtitle}</p>
    </section>
  );
}

function StatusLine({ label }: { label: string }) {
  return (
    <div className="statusline">
      <i />
      {label}
      <b>READY</b>
    </div>
  );
}

function InfoCard({ eyebrow, title, body }: { eyebrow: string; title: string; body: string }) {
  return (
    <Panel>
      <span className="label">{eyebrow}</span>
      <h3>{title}</h3>
      <p>{body}</p>
    </Panel>
  );
}

function Modal({
  title, close, children, wide = false,
}: {
  title: string; close: () => void; children: React.ReactNode; wide?: boolean;
}) {
  return (
    <div className="modalback" role="dialog" aria-modal="true">
      <section className={'modal ' + (wide ? 'wide' : '')}>
        <button className="close" onClick={close} aria-label="Close">×</button>
        <span className="label">TERRASR</span>
        <h2>{title}</h2>
        {children}
      </section>
    </div>
  );
}

// ─── Page: Dashboard ──────────────────────────────────────────────────────────
function Dashboard({
  s, observed, sr, go,
}: {
  s: Any; observed: string; sr: string; go: (p: Page) => void;
}) {
  return (
    <>
      {/* Hero: three-question story */}
      <section className="db-hero">
        <div className="db-hero-text">
          <span className="label">TERRASR · DEMONSTRATION MODE</span>
          <h1>10 m → Sub-4 m<br />Model-Reconstructed Target</h1>
          <p>
            Quality-aware multispectral preprocessing · Multispectral SwinIR reconstruction ·
            Validation, uncertainty, and downstream Earth-observation interpretation.
          </p>
          <div className="db-pipeline">
            <div className="db-pipe-step">
              <span className="label">INPUT</span>
              <strong>10 m Sentinel-2 L2A</strong>
              <small>B02 · B03 · B04 · B08</small>
            </div>
            <div className="db-pipe-arrow">↓</div>
            <div className="db-pipe-step highlight">
              <span className="label">MODEL</span>
              <strong>Multispectral SwinIR</strong>
              <small>Spatial reconstruction</small>
            </div>
            <div className="db-pipe-arrow">↓</div>
            <div className="db-pipe-step">
              <span className="label">TARGET</span>
              <strong>Sub-4 m Reconstructed</strong>
              <small>Prototype SR preview</small>
            </div>
          </div>
          <div className="db-actions">
            <button className="primary" onClick={() => go('Acquire')}>RUN ANALYSIS</button>
            <button className="minor" onClick={() => go('Acquire')}>CHANGE SCENE</button>
          </div>
        </div>
        <div className="db-hero-images">
          <span className="label">SELECTED SCENE · {s.name || 'Loading…'}</span>
          <div className="twins">
            {observed && (
              <figure>
                <img src={observed} alt="10 m observed input" />
                <figcaption>10 m OBSERVED</figcaption>
              </figure>
            )}
            {sr && (
              <figure>
                <img src={sr} alt="SR prototype preview" />
                <figcaption>SUB-4 m MODEL-RECONSTRUCTED TARGET</figcaption>
              </figure>
            )}
          </div>
          <DemoBadge>PROTOTYPE SR PREVIEW · deterministic enhancement · trained SwinIR not yet run</DemoBadge>
        </div>
      </section>

      {/* Status row */}
      <section className="db-status-row">
        <Panel className="db-status-panel">
          <span className="label">PIPELINE STATUS</span>
          <StatusLine label="Scene acquired" />
          <StatusLine label="Quality-aware preprocessing" />
          <StatusLine label="Prototype SR preview" />
          <StatusLine label="Validation and uncertainty" />
        </Panel>
        <Panel>
          <span className="label">SCENE</span>
          <h3>{s.name || SCENE_NAMES['urban']}</h3>
          <p>{s.location}</p>
          <p>{s.date} · Cloud {s.cloud_cover ?? CLOUD_COVER['urban']}% · {s.resolution || '10 m'} · {s.crs || 'EPSG:4326'}</p>
          <Badge>DEMO DATA</Badge>
        </Panel>
        <Panel>
          <span className="label">DOWNSTREAM</span>
          <div className="db-downstream">
            <button className="minor" onClick={() => go('Validate')}>Validation</button>
            <button className="minor" onClick={() => go('Uncertainty')}>Uncertainty</button>
            <button className="minor" onClick={() => go('Analysis')}>Applications</button>
            <button className="minor" onClick={() => go('AI Analyst')}>AI Analyst</button>
          </div>
        </Panel>
      </section>

      {/* Four-card footer */}
      <section className="fourcards">
        <InfoCard eyebrow="INPUT"       title="Sentinel-2 L2A"         body="10 m observed multispectral imagery" />
        <InfoCard eyebrow="TARGET"      title="Sub-4 m"                body="Model-reconstructed, not directly observed" />
        <InfoCard eyebrow="MODEL"       title="Multispectral SwinIR"   body="Production integration point · prototype preview active" />
        <InfoCard eyebrow="RELIABILITY" title="Validation + Uncertainty" body="Independent high-resolution reference required" />
      </section>
    </>
  );
}

// ─── Page: Acquire ────────────────────────────────────────────────────────────
function Acquire({
  data, selected, chosen, refresh,
}: {
  data: Any; selected: (s: string) => void; chosen: string; refresh: () => void;
}) {
  return (
    <>
      <Head
        eyebrow="01 / ACQUIRE"
        title="Scene Acquisition"
        subtitle="Select the Earth observation scene to analyze. All subsequent stages use this scene."
      />
      <section className="acquire">
        <Panel className="controls">
          <Badge>{data.source || 'COPERNICUS — DEMO'}</Badge>
          <h3>AOI / Scene Controls</h3>
          <label>
            Location
            <input value="Demonstration AOI" readOnly />
          </label>
          <label>
            Date range
            <input value="2025 demonstration scenes" readOnly />
          </label>
          <label>
            Maximum cloud cover
            <input value="10 %" readOnly />
          </label>
          <button className="primary full" onClick={refresh}>SEARCH SCENES</button>
          <button className="minor full" onClick={() => selected(chosen)}>USE DEMO SCENE</button>
          <p>{data.notice}</p>
        </Panel>

        <Panel className="demomap">
          <span className="label">SPATIAL CONTEXT</span>
          <div className="mapgrid">
            <b>DEMO AOI</b>
            <span>Sentinel-2 L2A catalogue contract</span>
          </div>
          <p>Offline demonstration dataset active. Live metadata is never mixed with demo imagery.</p>
        </Panel>

        <div className="results">
          {(data.scenes || []).map((s: Any) => (
            <Panel key={s.id} className={chosen === s.id ? 'selected' : ''}>
              <DemoBadge>{s.mode || 'DEMO DATA'}</DemoBadge>
              <h3>{s.name}</h3>
              <p>{s.location}</p>
              <p>{s.date} · Cloud {s.cloud_cover}% · {s.resolution} · {s.crs}</p>
              <button
                className={chosen === s.id ? 'minor' : 'primary'}
                onClick={() => selected(s.id)}
              >
                {chosen === s.id ? '✓ SCENE SELECTED' : 'SELECT SCENE'}
              </button>
            </Panel>
          ))}
        </div>
      </section>
    </>
  );
}

// ─── Page: Preprocess ─────────────────────────────────────────────────────────
function Preprocess({ data }: { data: Any }) {
  return (
    <>
      <Head
        eyebrow="03 / PREPROCESS"
        title="Preparing the Multispectral Input"
        subtitle="Quality-controlled B02/B03/B04/B08 for a consistent reconstruction workflow."
      />
      <section className="pretop">
        <Panel>
          <span className="label">INPUT</span>
          <h3>{data.input || 'Sentinel-2 L2A · 10 m'}</h3>
        </Panel>
        <Panel>
          <span className="label">SELECTED BANDS</span>
          <div className="bands">
            {(data.bands || ['B02', 'B03', 'B04', 'B08']).map((b: string) => (
              <Badge key={b}>{b}</Badge>
            ))}
          </div>
        </Panel>
        <details>
          <summary>Why these bands?</summary>
          <p>
            <b>B02</b> Blue · <b>B03</b> Green · <b>B04</b> Red · <b>B08</b> Near Infrared.
            These four bands provide the multispectral signal used by the prototype SR pipeline.
          </p>
        </details>
      </section>

      <section className="steps">
        {(data.steps || []).map((x: Any) => (
          <Panel key={x.id}>
            <Badge>{x.id} · {x.status}</Badge>
            <h3>{x.name}</h3>
            <p><b>Purpose:</b> {x.purpose}</p>
            <p><b>Output:</b> {x.output}</p>
          </Panel>
        ))}
      </section>

      <Panel className="console">
        <span className="label">PROCESSING LOG</span>
        {(data.logs || []).map((x: string) => (
          <p key={x}>✓ {x}</p>
        ))}
      </Panel>
    </>
  );
}

// ─── Page: SR Engine ──────────────────────────────────────────────────────────
function SR({
  data, slider, setSlider,
}: {
  data: Any; slider: number; setSlider: (n: number) => void;
}) {
  return (
    <>
      <Head
        eyebrow="04 / RECONSTRUCT"
        title="Multispectral Super-Resolution"
        subtitle="Reconstructing fine-scale spatial detail from multispectral Sentinel-2 observations."
      />

      {/* Spec strip */}
      <section className="strip">
        <InfoCard eyebrow="INPUT"  title="10 m"                    body="Observed Sentinel-2 L2A" />
        <InfoCard eyebrow="BANDS"  title="B02 / B03 / B04 / B08"   body="Multispectral input stack" />
        <InfoCard eyebrow="MODEL"  title="Multispectral SwinIR"    body="Production engine · prototype preview active" />
        <InfoCard eyebrow="TARGET" title="Sub-4 m"                 body="Model-reconstructed target" />
      </section>

      {/* Hero comparison slider */}
      <Panel className="viewer">
        <div className="base">
          {data.observed && <img src={data.observed} alt="10 m observed" />}
          <b>ORIGINAL · 10 m OBSERVED</b>
        </div>
        <div className="reveal" style={{ width: slider + '%' }}>
          {data.sr_preview && <img src={data.sr_preview} alt="SR prototype preview" />}
          <b>SR PREVIEW · SUB-4 m MODEL-RECONSTRUCTED TARGET</b>
        </div>
        <input
          aria-label="Compare original and SR preview"
          type="range"
          min="0"
          max="100"
          value={slider}
          onChange={e => setSlider(+e.target.value)}
        />
      </Panel>

      {/* Disclosure panels */}
      <section className="explain">
        <Panel>
          <DemoBadge>PROTOTYPE SR PREVIEW</DemoBadge>
          <p style={{ marginTop: 10 }}>{data.real_swinir}</p>
          <p style={{ marginTop: 8, fontSize: 12, color: '#8fb0b8' }}>
            Fine-scale content shown here is model-inferred and should be independently validated before operational use.
          </p>
        </Panel>
        <Panel>
          <span className="label">MODEL PIPELINE</span>
          <p>
            B02/B03/B04/B08 → Shallow feature extraction → Residual Swin Transformer Blocks (RSTB) →
            Deep feature reconstruction → Pixel-shuffle upsampling → Sub-4 m SR output
          </p>
          <p style={{ marginTop: 10 }}>
            <b>SwinIR</b> uses shifted-window self-attention within each RSTB for long-range spatial dependency modelling.&nbsp;
            <b>RCAN</b> (Residual Channel Attention Network) is the planned CNN baseline evaluation.&nbsp;
            <b>Nemotron</b> is the EO reasoning and orchestration layer — separate from image reconstruction.
          </p>
          {data.baseline_note && (
            <p style={{ marginTop: 8, fontSize: 12, color: '#8fb0b8' }}>{data.baseline_note}</p>
          )}
        </Panel>
      </section>
    </>
  );
}

// ─── Page: Validate ───────────────────────────────────────────────────────────
function Validate({ data }: { data: Any }) {
  const GROUPS = ['Spatial fidelity', 'Spectral fidelity'];
  return (
    <>
      <Head
        eyebrow="05 / VALIDATE"
        title="Scientific Validation"
        subtitle="How do we know the reconstruction is useful?"
      />
      <DemoBadge>ALL VALUES · DEMO / ILLUSTRATIVE · not measured from real HR reference</DemoBadge>

      {GROUPS.map(g => (
        <section className="metricgroup" key={g}>
          <h2>{g}</h2>
          <div>
            {(data.metrics || [])
              .filter((x: Any) => x.group === g)
              .map((x: Any) => (
                <Panel key={x.name}>
                  <span className="label" title={x.help}>{x.name} ⓘ</span>
                  <h2>{x.value}</h2>
                  <DemoBadge>DEMO VALUE</DemoBadge>
                  <p>{x.help}</p>
                </Panel>
              ))}
          </div>
        </section>
      ))}

      <Panel>
        <span className="label">GEOSPATIAL CONSISTENCY</span>
        <div className="tags">
          {(data.geospatial || []).map((x: string) => (
            <Badge key={x}>{x}</Badge>
          ))}
        </div>
      </Panel>
    </>
  );
}

// ─── Page: Uncertainty ────────────────────────────────────────────────────────
function Uncertainty({ data }: { data: Any }) {
  return (
    <>
      <Head
        eyebrow="06 / UNCERTAINTY"
        title="Reconstruction Uncertainty"
        subtitle="Not every reconstructed detail is equally reliable."
      />
      <section className="uncert">
        <Panel className="uncimage">
          {data.uncertainty_image && (
            <img src={data.uncertainty_image} alt="Uncertainty heatmap" />
          )}
          <div>
            <DemoBadge>PROTOTYPE VISUALIZATION</DemoBadge>
            <p>LOW · MEDIUM · HIGH</p>
          </div>
        </Panel>
        <Panel>
          <h3>{data.mean}</h3>
          <p>Mean uncertainty</p>
          <h3>{data.p95}</h3>
          <p>P95 uncertainty</p>
          <h3>{data.region}</h3>
          <p>{(data.focus || []).join(' · ')}</p>
        </Panel>
      </section>
      <Panel className="warning">
        <b>{data.note}</b>
      </Panel>
    </>
  );
}

// ─── Page: Analysis ───────────────────────────────────────────────────────────
function Analysis({ scene, data }: { scene: string; data: Any }) {
  const cards = [
    {
      id: 'AGRICULTURE',
      workflow: 'SR preview → NDVI → vegetation interpretation',
      analysis: scene === 'agriculture' ? data.result : 'Vegetation-focused screening with B08 and B04.',
      uncertainty: scene === 'agriculture' ? data.uncertainty : 'DEMO ANALYTICS',
      extra: scene === 'agriculture' && data.ndvi
        ? `NDVI: ${data.ndvi} · ${data.formula}` : null,
    },
    {
      id: 'URBAN',
      workflow: 'SR preview → feature visibility → urban interpretation',
      analysis: scene === 'urban' ? data.result : 'Improved visual interpretability; not guaranteed extraction.',
      uncertainty: scene === 'urban' ? data.uncertainty : 'DEMO ANALYTICS',
      extra: null,
    },
    {
      id: 'DISASTER',
      workflow: 'Pre-event + Post-event → change → potential regions',
      analysis: scene === 'disaster' ? 'Pre/post context supports qualitative change screening.' : 'DEMO ANALYSIS',
      uncertainty: 'Boundary uncertainty requires reference validation.',
      extra: null,
    },
    {
      id: 'CHANGE DETECTION',
      workflow: 'Scene A + Scene B → co-registration → difference map',
      analysis: 'Potential change areas are illustrative.',
      uncertainty: 'DEMO ANALYSIS',
      extra: null,
    },
  ];

  return (
    <>
      <Head
        eyebrow="07 / ANALYZE"
        title="Downstream EO Applications"
        subtitle="Application outputs remain explicitly uncertainty-aware and illustrative."
      />
      <section className="applications">
        {cards.map(c => (
          <Panel key={c.id}>
            <Badge>{c.id}</Badge>
            <h3>{c.workflow}</h3>
            <p><b>Analysis:</b> {c.analysis}</p>
            <p><b>Uncertainty:</b> {c.uncertainty}</p>
            {c.extra && <p><b>{c.extra}</b></p>}
          </Panel>
        ))}
      </section>
    </>
  );
}

// ─── Page: AI Analyst ─────────────────────────────────────────────────────────
function Analyst({
  scene, data, setData, go,
}: {
  scene: string; data: Any; setData: (d: Any) => void; go: (p: Page) => void;
}) {
  const ask = async (prompt: string) => {
    try {
      setData(await api('/nemotron/analyze', { scene_id: scene, prompt }));
    } catch {
      /* keep current data */
    }
  };

  return (
    <>
      <Head
        eyebrow="08 / EXPLAIN"
        title="TerraSR EO Analyst"
        subtitle="NVIDIA Nemotron 3 Ultra · Earth Observation reasoning and orchestration layer"
      />
      <section className="context">
        {['Scene Context', 'Observation Quality', 'SR Notes', 'Spectral', 'Uncertainty', 'Findings'].map(x => (
          <Badge key={x}>{x}</Badge>
        ))}
      </section>

      <Panel className="analyst">
        <Badge>{data.mode || 'DEMO ANALYST'}</Badge>
        <h2>{data.model || 'NVIDIA Nemotron 3 Ultra'}</h2>
        <p style={{ whiteSpace: 'pre-wrap' }}>{data.response || 'Select an action to generate a structured scene analysis.'}</p>
        <div className="actiongrid">
          {[
            'Analyze Scene',
            'Explain Spectral Quality',
            'Explain Uncertainty',
            'Recommend Application',
            'Generate Report',
          ].map(x => (
            <button key={x} className="minor" onClick={() => ask(x)}>{x}</button>
          ))}
          <button className="primary" onClick={() => go('Report')}>VIEW SCENE REPORT</button>
        </div>
      </Panel>

      <section className="roles">
        <Panel>
          <span className="label">SWINIR</span>
          <h3>Spatial super-resolution</h3>
          <p>Residual Swin Transformer Blocks reconstruct fine-scale spatial detail from multispectral Sentinel-2 input.</p>
        </Panel>
        <Panel>
          <span className="label">NEMOTRON</span>
          <h3>EO reasoning · orchestration · reporting</h3>
          <p>Interprets pipeline outputs using structured EO-analyst framing — scene context, spectral quality, uncertainty types, and actionable recommendations.</p>
        </Panel>
      </section>
    </>
  );
}


// ─── Page: Architecture ───────────────────────────────────────────────────────
const ARCH_NODES = [
  { top: 'DATA SOURCE',    body: 'Copernicus\nSentinel-2 L2A\n10 m GSD' },
  { top: 'PREPROCESSING', body: 'SCL cloud mask\nBand alignment\nReflectance norm.' },
  { top: 'MULTISPECTRAL', body: 'B02 · B03\nB04 · B08\n[B, 4, H, W] tensor' },
  { top: 'SWINIR',        body: 'RSTB blocks\nShifted-window\nattention' },
  { top: 'SR PRODUCT',    body: 'Sub-4 m\nreconstructed\ntarget' },
  { top: 'VALIDATION',    body: 'PSNR / SSIM\nSAM / ERGAS / RMSE' },
  { top: 'UNCERTAINTY',   body: 'Aleatoric\nEpistemic\nreliability map' },
  { top: 'APPLICATIONS',  body: 'Agriculture\nUrban · Disaster' },
  { top: 'NEMOTRON',      body: 'EO reasoning\norchestration\nreporting' },
];

function Architecture() {
  return (
    <>
      <Head
        eyebrow="SYSTEM OVERVIEW"
        title="TerraSR Architecture"
        subtitle="Sentinel-2 L2A → Multispectral SwinIR SR → Validation → Uncertainty → EO Applications"
      />
      <section className="architecture">
        {ARCH_NODES.map(n => (
          <div key={n.top}>
            <p>{n.top}</p>
            {n.body.split('\n').map(line => <p key={line}>{line}</p>)}
          </div>
        ))}
      </section>
      <section className="roles" style={{ marginTop: 20 }}>
        <Panel>
          <span className="label">SWINIR · PRIMARY SR ENGINE</span>
          <h3>Spatial super-resolution via Residual Swin Transformer Blocks</h3>
          <p>
            Takes a 4-band multispectral input tensor [B, 4, H, W] (B02/B03/B04/B08) and reconstructs a sub-4 m target.
            Shifted-window self-attention captures long-range spatial dependencies with linear computational complexity.
            Reference: Liang et al., <em>SwinIR: Image Restoration Using Swin Transformer</em>, ICCVW 2021.
          </p>
        </Panel>
        <Panel>
          <span className="label">RCAN · CNN BASELINE</span>
          <h3>Residual Channel Attention Network — planned evaluation</h3>
          <p>
            RCAN (Zhang et al., ECCV 2018) uses Residual-in-Residual structure with channel attention.
            It will be evaluated as the CNN baseline against SwinIR on the same dataset, preprocessing,
            and validation protocol (PSNR / SSIM / SAM / ERGAS).
          </p>
        </Panel>
        <Panel>
          <span className="label">NEMOTRON · REASONING LAYER</span>
          <h3>EO reasoning · orchestration · reporting</h3>
          <p>Interprets all pipeline outputs. Structures analysis as: scene context, observation quality, SR product notes, spectral considerations, uncertainty (aleatoric vs. epistemic), key finding, and recommended action. Does NOT perform image super-resolution.</p>
        </Panel>
      </section>
    </>
  );
}


// ─── Page: Report ─────────────────────────────────────────────────────────────
function Report({
  data, download,
}: {
  data: Any; download: (k: 'json' | 'csv') => void;
}) {
  return (
    <>
      <Head eyebrow="REPORT" title="TerraSR Scene Analysis Report" subtitle="A concise, portable summary of the selected-scene workflow." />
      <Panel className="report">
        <DemoBadge>PROTOTYPE DEMONSTRATION</DemoBadge>
        <pre>{data.markdown || 'Generating report…'}</pre>
        <div className="actions">
          <button className="minor" onClick={() => download('json')}>EXPORT JSON</button>
          <button className="minor" onClick={() => download('csv')}>EXPORT CSV</button>
        </div>
      </Panel>
    </>
  );
}

// ─── Page: About ─────────────────────────────────────────────────────────────
function About() {
  const items: [string, string][] = [
    ['Problem Statement',   'SIH 2026 · SIH26142 · NTRO: Deep Learning Based Super Resolution Mapping (SRM) from medium-resolution satellite imagery.'],
    ['Approach',            'Quality-aware multispectral preprocessing → Multispectral SwinIR reconstruction → Spatial / spectral validation → Uncertainty quantification → Downstream EO applications.'],
    ['Why SwinIR',          'Residual Swin Transformer Blocks (RSTB) capture long-range spatial dependencies via shifted-window self-attention — superior to CNN-only approaches for texture-rich EO scenes while reducing parameter count by up to 67% versus deeper CNNs (Liang et al., ICCVW 2021).'],
    ['CNN Baseline',        'RCAN (Residual Channel Attention Network, Zhang et al. ECCV 2018) will be trained and evaluated alongside SwinIR on the same multispectral dataset and validation protocol. Channel attention allows the network to selectively weight informative spectral bands.'],
    ['Sensor-Aware Design', 'Degradation model follows the Sentinel-2 sensor modulation transfer function (MTF). Training on synthetic downscaled HR imagery (similar to DSen2, Lanaras et al. 2018 ISPRS) avoids the need for unavailable paired HR/LR ground truth.'],
    ['Bands',               'B02 (Blue 490 nm) · B03 (Green 560 nm) · B04 (Red 665 nm) · B08 (NIR 842 nm) — all native 10 m Sentinel-2 L2A bands. Tensor input: [B, 4, H, W].'],
    ['Validation Protocol', 'PSNR (spatial), SSIM (structural), RMSE (error), SAM (spectral-angle), ERGAS (global spectral error). Production validation requires co-registered SPOT-6/7 or equivalent 1.5 m reference imagery.'],
    ['Uncertainty',         'Aleatoric (observation noise, mixed pixels) and epistemic (model limitations) uncertainty. Production plan: Monte Carlo ensemble variance or stochastic test-time dropout.'],
    ['Prototype Status',    'PROTOTYPE — deterministic Lanczos + edge enhancement. Trained SwinIR inference is the production integration target.'],
    ['Technology',          'FastAPI · React 19 · Vite · Sentinel-2 L2A (ESA Copernicus) · SwinIR / RCAN · NVIDIA Nemotron 3 Ultra.'],
    ['Production Roadmap',  'Paired HR/LR dataset → Multispectral SwinIR + RCAN training → Benchmark evaluation → Bayesian uncertainty → Live Copernicus API → Autonomous Nemotron tool calling.'],
  ];
  return (
    <>
      <Head eyebrow="ABOUT" title="TerraSR" subtitle="Multispectral Earth Observation Super-Resolution · SIH 2026 · SIH26142" />
      <section className="about">
        {items.map(([k, v]) => (
          <Panel key={k}>
            <span className="label">{k}</span>
            <p>{v}</p>
          </Panel>
        ))}
      </section>
    </>
  );
}

// ─── Root App ─────────────────────────────────────────────────────────────────
function App() {
  const [page, setPage]     = useState<Page>('Dashboard');
  const [scene, setScene]   = useState(() => localStorage.getItem('terrasr-scene') || 'urban');
  const [data, setData]     = useState<Any>({});
  const [health, setHealth] = useState<Any>({ data: 'demo', nemotron: 'demo', pipeline: 'ready' });
  const [help, setHelp]     = useState(false);
  const [notes, setNotes]   = useState(false);
  const [judge, setJudge]   = useState(false);
  const [auto, setAuto]     = useState(false);
  const [step, setStep]     = useState(0);
  const [slider, setSlider] = useState(50);
  const [message, setMessage] = useState('');

  // Fetch data whenever page or scene changes
  const load = async () => {
    try {
      const endpoint = PAGE_ROUTE[page];
      if (endpoint) {
        setData(await api(endpoint, { scene_id: scene, prompt: 'Analyze Scene' }));
      }
    } catch {
      setMessage('Local API unavailable. Start run.bat and refresh.');
    }
  };

  useEffect(() => { api('/health').then(setHealth).catch(() => {}); }, []);
  useEffect(() => { localStorage.setItem('terrasr-scene', scene); load(); }, [page, scene]);

  // Judge Mode auto-advance
  useEffect(() => {
    if (!judge || !auto) return;
    const id = setInterval(() => {
      setStep(i => {
        const next = i + 1;
        if (next >= WORKFLOW.length) { setAuto(false); return i; }
        setPage(WORKFLOW[next][0]);
        return next;
      });
    }, 6000);
    return () => clearInterval(id);
  }, [judge, auto]);

  const selectScene = (s: string) => {
    setScene(s);
    setMessage(`✓ ${SCENE_NAMES[s]} selected. Continue to preprocessing.`);
  };

  const judgeNext = () => {
    const n = Math.min(step + 1, WORKFLOW.length - 1);
    setStep(n);
    setPage(WORKFLOW[n][0]);
  };

  const judgeRestart = () => { setStep(0); setAuto(false); setPage('Acquire'); };

  const startJudge = () => { setJudge(true); setStep(0); setPage('Acquire'); };

  const current   = data.scene || data.metadata || {};
  const observed  = data.observed;
  const sr        = data.sr_preview;

  const download = (kind: 'json' | 'csv') => {
    const text = kind === 'json'
      ? JSON.stringify({ scene: current, report: data }, null, 2)
      : `field,value\nScene,"${current.name || SCENE_NAMES[scene]}"\nStatus,Prototype Demonstration\nTarget,Sub-4 m model-reconstructed target\n`;
    const a = document.createElement('a');
    a.href = URL.createObjectURL(new Blob([text], { type: 'text/' + kind }));
    a.download = `TerraSR_${scene}_report.${kind}`;
    a.click();
    URL.revokeObjectURL(a.href);
  };

  return (
    <div className="shell">
      {/* ── Header ── */}
      <header className="top">
        <button className="wordmark" onClick={() => setPage('Dashboard')}>
          <b>Terra<span>SR</span></b>
          <small>Multispectral Earth Observation Super-Resolution Platform</small>
        </button>
        <div className="topright">
          <div className="statuses">
            <Chip>DATA · {health.data?.toUpperCase()}</Chip>
            <Chip>SR · PROTOTYPE</Chip>
            <Chip>AI · {health.nemotron?.toUpperCase()}</Chip>
            <Chip>PIPELINE · {health.pipeline?.toUpperCase()}</Chip>
          </div>
          <button className="minor" onClick={() => setHelp(true)}>How it works</button>
          <button className="primary" onClick={startJudge}>JUDGE MODE</button>
        </div>
      </header>

      {/* ── Nav ── */}
      <div className="navrow">
        <nav>
          {NAV_PAGES.map(x => (
            <button key={x} className={page === x ? 'current' : ''} onClick={() => setPage(x)}>
              {x}
            </button>
          ))}
        </nav>
        <button className="scenechip" onClick={() => setPage('Acquire')}>
          <b>CURRENT SCENE</b>{' '}
          {SCENE_NAMES[scene]} · 10 m · L2A · Cloud{' '}
          {(current.cloud_cover ?? CLOUD_COVER[scene])}%
        </button>
      </div>

      {/* ── Main content ── */}
      <main>
        {message && (
          <div className="notice">
            {message}
            <button onClick={() => setMessage('')}>×</button>
          </div>
        )}

        {page === 'Dashboard'   && <Dashboard s={current} observed={observed} sr={sr} go={setPage} />}
        {page === 'Acquire'     && <Acquire data={data} selected={selectScene} chosen={scene} refresh={load} />}
        {page === 'Preprocess'  && <Preprocess data={data} />}
        {page === 'SR Engine'   && <SR data={data} slider={slider} setSlider={setSlider} />}
        {page === 'Validate'    && <Validate data={data} />}
        {page === 'Uncertainty' && <Uncertainty data={data} />}
        {page === 'Analysis'    && <Analysis scene={scene} data={data} />}
        {page === 'AI Analyst'  && <Analyst scene={scene} data={data} setData={setData} go={setPage} />}
        {page === 'Architecture'&& <Architecture />}
        {page === 'Report'      && <Report data={data} download={download} />}
        {page === 'About'       && <About />}
      </main>

      {/* ── Footer ── */}
      <footer>
        <span>Multispectral Earth Observation Super-Resolution · SIH 2026 · SIH26142</span>
        <button onClick={() => setNotes(true)}>Presenter notes</button>
        <button onClick={() => setPage('About')}>About TerraSR</button>
        <span>Prototype for SIH 2026 • NTRO Problem Statement SIH26142</span>
      </footer>

      {/* ── Modals ── */}
      {help && (
        <Modal title="How TerraSR works" close={() => setHelp(false)}>
          <ol>
            {[
              'We acquire 10 m Sentinel-2 L2A imagery.',
              'We quality-control and align multispectral bands.',
              'We prepare the input for super-resolution.',
              'SwinIR reconstructs fine-scale spatial detail.',
              'We evaluate spatial and spectral fidelity.',
              'We quantify reconstruction uncertainty.',
              'We use the result for downstream EO interpretation.',
              'Nemotron interprets and orchestrates the workflow.',
            ].map(x => <li key={x}>{x}</li>)}
          </ol>
        </Modal>
      )}

      {notes && (
        <Modal title="Presenter notes" close={() => setNotes(false)}>
          <p>First, we select a Sentinel-2 L2A scene at 10 m.</p>
          <p>Next, the system performs cloud masking, band extraction, alignment and normalization.</p>
          <p>We prepare the B02, B03, B04 and B08 multispectral input.</p>
          <p>Our production model is multispectral SwinIR, which reconstructs a sub-4 m target product.</p>
          <p>We do not treat reconstructed detail as direct observation.</p>
          <p>So we evaluate spatial and spectral fidelity and generate uncertainty.</p>
          <p>Finally, the reconstructed product can support agriculture, urban, disaster and change-analysis workflows. Nemotron acts as the reasoning and orchestration layer.</p>
        </Modal>
      )}

      {judge && (
        <Modal title="TerraSR Judge Mode" close={() => { setJudge(false); setAuto(false); }} wide>
          <div className="timeline">
            {WORKFLOW.map((x, i) => (
              <button
                key={x[1]}
                className={i === step ? 'active' : i < step ? 'done' : ''}
                onClick={() => { setStep(i); setPage(x[0]); }}
              >
                <b>{String(i + 1).padStart(2, '0')}</b>{x[1]}
              </button>
            ))}
          </div>
          <div className="judgecopy">
            <Badge>STEP {String(step + 1).padStart(2, '0')} — {WORKFLOW[step][1].toUpperCase()}</Badge>
            <h2>{WORKFLOW[step][2]}</h2>
            <p><b>Why it matters:</b> {WORKFLOW[step][3]}</p>
            <p><b>Result:</b> {SCENE_NAMES[scene]} remains the single scene used throughout this guided demonstration.</p>
          </div>
          <div className="actions">
            <button className="minor" onClick={judgeRestart}>RESTART</button>
            <button className="minor" onClick={() => setAuto(!auto)}>
              {auto ? 'PAUSE' : 'AUTO RUN · ~48 SEC'}
            </button>
            <button className="primary" onClick={judgeNext}>NEXT STEP</button>
          </div>
        </Modal>
      )}
    </div>
  );
}

createRoot(document.getElementById('root')!).render(<App />);
