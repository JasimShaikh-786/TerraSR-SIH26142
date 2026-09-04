import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch

def create_diagram():
    fig = plt.figure(figsize=(18, 10.5), dpi=150, facecolor='#07141c')
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_facecolor('#07141c')
    ax.set_xlim(0, 1800)
    ax.set_ylim(0, 1050)
    ax.axis('off')

    # Background subtle grid pattern
    for x in range(0, 1800, 60):
        ax.plot([x, x], [0, 1050], color='#0e2533', linewidth=0.5, alpha=0.3)
    for y in range(0, 1050, 60):
        ax.plot([0, 1800], [y, y], color='#0e2533', linewidth=0.5, alpha=0.3)

    # Header
    ax.text(900, 1005, "TerraSR · SYSTEM ARCHITECTURE", 
            ha='center', va='center', color='#63dbe8', fontsize=22, fontweight='bold', family='sans-serif')
    ax.text(900, 975, "Multispectral Super-Resolution Mapping & NVIDIA Nemotron AI Reasoning Pipeline (SIH26142)", 
            ha='center', va='center', color='#9bbecd', fontsize=12, family='sans-serif')

    # Container 1: Remote Sensing & Deep Learning Pipeline
    box1 = FancyBboxPatch((40, 150), 1200, 780, boxstyle="round,pad=10,rounding_size=15",
                          facecolor='#0a1d27', edgecolor='#1f5869', linewidth=1.5)
    ax.add_patch(box1)
    
    # Title badge for Container 1
    badge1 = FancyBboxPatch((60, 890), 550, 36, boxstyle="round,pad=5,rounding_size=8",
                            facecolor='#103947', edgecolor='#4bd4e4', linewidth=1)
    ax.add_patch(badge1)
    ax.text(75, 908, "REMOTE SENSING & DEEP LEARNING (SwinIR Pipeline)", 
            va='center', color='#63dbe8', fontsize=11, fontweight='bold')

    # Container 2: AI Reasoning & Orchestration Layer (NVIDIA Nemotron)
    box2 = FancyBboxPatch((1270, 150), 490, 780, boxstyle="round,pad=10,rounding_size=15",
                          facecolor='#091c10', edgecolor='#2d6b38', linewidth=1.5)
    ax.add_patch(box2)

    # Title badge for Container 2
    badge2 = FancyBboxPatch((1290, 890), 450, 36, boxstyle="round,pad=5,rounding_size=8",
                            facecolor='#123d1d', edgecolor='#76b900', linewidth=1)
    ax.add_patch(badge2)
    ax.text(1305, 908, "AI REASONING & ORCHESTRATION (Nemotron Layer)", 
            va='center', color='#9bee66', fontsize=11, fontweight='bold')

    # Helper function to draw node cards
    def draw_node(x, y, w, h, title, subtitle, details, bg='#0d2b38', border='#24667a', title_color='#eefcff'):
        card = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=6,rounding_size=8",
                              facecolor=bg, edgecolor=border, linewidth=1.2)
        ax.add_patch(card)
        ax.text(x + 14, y + h - 18, title, va='top', color=title_color, fontsize=11, fontweight='bold')
        ax.text(x + 14, y + h - 38, subtitle, va='top', color='#62dce8', fontsize=9, fontweight='semibold')
        for i, d in enumerate(details):
            ax.text(x + 14, y + h - 56 - (i * 15), "• " + d, va='top', color='#a2c4cc', fontsize=8.5)

    def draw_arrow(x1, y1, x2, y2, color='#4bd4e4', style='->', lw=2):
        ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                    arrowprops=dict(arrowstyle=style, color=color, lw=lw, 
                                   shrinkA=0, shrinkB=0, mutation_scale=15))

    # --- Column 1: Input & Ingestion (Inside Container 1) ---
    draw_node(70, 740, 240, 120, "1. Sentinel-2 L2A", "Medium-Resolution Input", 
              ["10 m GSD observations", "Bottom-Of-Atmosphere (BOA)", "12-bit multispectral tiles", "B02, B03, B04, B08 bands"])

    draw_arrow(190, 740, 190, 690)

    draw_node(70, 560, 240, 120, "2. Scene / AOI Selection", "Spatial Query & Metadata", 
              ["Bounding box coordinates", "Acquisition timestamps", "Sensor geometry & angles", "Persistent scene manifest"])

    draw_arrow(190, 560, 190, 510)

    draw_node(70, 380, 240, 120, "3. Quality Control (QC)", "Cloud & Artifact Filtering", 
              ["Scene Classification (SCL)", "Cloud & cirrus masking", "Cast shadow removal", "NoData verification"])

    draw_arrow(190, 380, 190, 330)

    draw_node(70, 200, 240, 120, "4. Multispectral Prep", "Radiometric Co-registration", 
              ["Sub-pixel spatial alignment", "Reflectance [0-10000] scaling", "Overlap patch extraction", "Georeferenced tensors"])

    # Connection from Col 1 to Col 2
    draw_arrow(320, 260, 370, 260)
    ax.text(345, 275, "4-Band\nStack", color='#4bd4e4', fontsize=8.5, fontweight='bold', ha='center')

    # --- Column 2: Super-Resolution Core (Inside Container 1) ---
    draw_node(370, 200, 270, 660, "5. Multispectral SwinIR Engine", "Spatial Transformer Reconstruction", 
              ["Residual Swin Transformer (RSTB)",
               "Shifted-Window Self-Attention (W-MSA)",
               "Hierarchical cross-patch representations",
               "4-Channel input: B02/B03/B04/B08",
               "4x Spatial sub-pixel upscaling",
               "Reflectance-preserving feature maps",
               "Patch extraction with 32 px overlap",
               "Gaussian-weighted seamless stitching",
               "High-frequency edge reconstruction",
               "Model-inferred spatial synthesis",
               "",
               "RECONSTRUCTED OUTPUT:",
               "Sub-4 m target multispectral product",
               "Preserved geospatial transforms & CRS",
               "Surface reflectance consistency"],
              bg='#103a4c', border='#4bd4e4', title_color='#ffffff')

    # Arrow from SR Engine to Validation & Uncertainty
    draw_arrow(650, 680, 700, 680)
    draw_arrow(650, 480, 700, 480)
    draw_arrow(650, 280, 700, 280)

    # --- Column 3: Quality Assurance & Downstream EO (Inside Container 1) ---
    draw_node(700, 600, 250, 160, "6A. Scientific Validation", "Quantitative Fidelity Metrics", 
              ["Spatial: PSNR, SSIM, RMSE", "Spectral: SAM (Spectral Angle)", "Radiometric: ERGAS index", "Geospatial coordinate alignment", "Target benchmark checks"])

    draw_node(700, 400, 250, 160, "6B. Uncertainty Estimation", "Spatial Reliability Mapping", 
              ["Gradient-based variance heatmap", "Edge boundary confidence", "High / Medium / Low zones", "Epistemic/Aleatoric framing", "Model inference disclosures"])

    draw_node(700, 200, 250, 160, "7. Downstream EO Tasks", "Decision-Ready Intelligence", 
              ["Precision Agriculture NDVI", "Urban Road & Building Edges", "Flood Inundation Delineation", "Multi-temporal Change Detection", "Illustrative screening indices"])

    # Connections to Container 2 (NVIDIA Nemotron)
    draw_arrow(960, 680, 1030, 680)
    draw_arrow(960, 480, 1030, 480)
    draw_arrow(960, 280, 1030, 280)

    # Aggregator Node before Nemotron
    draw_node(1030, 360, 190, 320, "Telemetry & Context", "Structured Pipeline Bus",
              ["Scene Metadata", "Validation Scores", "Uncertainty Stats", "Application Indices", "Geospatial BBox", "Pipeline State"],
              bg='#0f2a36', border='#2b6978')

    draw_arrow(1230, 520, 1310, 520, color='#76b900', lw=2.5)
    ax.text(1270, 540, "JSON Telemetry\n& Prompts", color='#9bee66', fontsize=8.5, fontweight='bold', ha='center')

    # --- Container 2: NVIDIA Nemotron Nodes ---
    draw_node(1310, 580, 410, 280, "8. NVIDIA Nemotron 3 Ultra", "Reasoning & Orchestration Engine",
              ["Model: nvidia/nemotron-3-ultra-550b-a55b",
               "OpenAI-compatible NVIDIA NGC API client",
               "Domain-specific EO system prompt",
               "Multi-modal prompt synthesis (metadata + metrics)",
               "Scientific validation explanation",
               "Uncertainty-aware confidence interpretation",
               "Autonomous pipeline task orchestration",
               "Offline fallback mode for judge demonstration"],
              bg='#0d2e16', border='#76b900', title_color='#c2ff85')

    draw_arrow(1515, 580, 1515, 480, color='#76b900', lw=2)

    draw_node(1310, 200, 410, 270, "9. AI Analyst Report & Export", "Synthesized Operational Delivery",
              ["Multi-section structured report:",
               "  1. Acquisition & Scene Telemetry",
               "  2. Quality Control & Preprocessing",
               "  3. SwinIR Reconstruction Summary",
               "  4. Scientific Validation Disclosure",
               "  5. Uncertainty & Limitation Warnings",
               "  6. Actionable Application Insights",
               "Export formats: Markdown, JSON, CSV",
               "Direct judge mode walk-through guidance"],
              bg='#0f361a', border='#459e2b', title_color='#ffffff')

    # Legend / Disclaimer Card at Bottom
    legend = FancyBboxPatch((40, 40), 1720, 80, boxstyle="round,pad=8,rounding_size=10",
                            facecolor='#0b1a22', edgecolor='#254b57', linewidth=1)
    ax.add_patch(legend)
    
    ax.text(70, 95, "TECHNICAL ARCHITECTURE & ROLE SEPARATION STATEMENT:", 
            color='#f0c060', fontsize=10, fontweight='bold')
    ax.text(70, 68, "- SwinIR: Performs deep-learning spatial reconstruction directly on multispectral pixels (B02/B03/B04/B08) from 10 m to sub-4 m target.\n- NVIDIA Nemotron: Reasoning, orchestration, and reporting layer. It does NOT process raw image pixels; it reasons over structured pipeline telemetry and outputs.", 
            color='#bddbe1', fontsize=9)

    plt.savefig('docs/images/architecture.png', dpi=150, bbox_inches='tight', pad_inches=0.1)
    print("architecture.png created successfully!")

if __name__ == '__main__':
    create_diagram()
