# Epistemic Engine - Quick Start Guide

## 🚀 Running the Epistemic Engine

### Prerequisites
- OpenSpace 0.19+ installed
- PostgreSQL 15+ with PostGIS (for data ingestion)
- Python 3.7+ with dependencies installed

---

## 📦 Installation

### 1. Install Python Dependencies
```bash
cd Epistemic-Engine
pip3 install --user -r requirements.txt
```

### 2. Set Up Database (Optional - for data ingestion)
```bash
# Create database
createdb epistemic_engine

# Apply schema
psql epistemic_engine < src/db/schema.sql
```

### 3. Generate Data Files

**Option A: Automated (Recommended)**
```bash
# Generate all data files in one command
python3 run_pipeline.py

# Or run specific phases:
python3 run_pipeline.py --phases 1,4  # Kinematics + Laniakea only

# See what would be executed without running:
python3 run_pipeline.py --dry-run
```

**Option B: Manual (Individual Scripts)**
```bash
# Phase 1: Generate Sun's orbit and CMB arrow
python3 src/ingestion/generate_sun_path.py --samples 1000 --output-dir data/sun_orbit
python3 src/ingestion/generate_cmb_arrow.py --output-dir data/cmb_vector

# Phase 4: Generate Laniakea structure  
python3 src/ingestion/generate_laniakea.py --galaxies 5000 --output-dir data/laniakea
```

**Option C: With Database (Full Pipeline)**
```bash
# Phase 2: Ingest Gaia data (optional - requires database)
python3 src/ingestion/ingest_gaia.py --limit 100000 --test
python3 src/ingestion/export_to_speck.py --output data/gaia_observed.speck

# Or use orchestrator with database steps:
python3 run_pipeline.py --with-database
```

---

## 🎮 Controls (Truth Slider)

| Key | Mode | Description | Layers Visible |
|:---:|:-----|:------------|:---------------|
| **1** | **OBSERVED** | Direct measurements with error bars | L0 only (Blue/White) |
| **2** | **INFERRED** | Models derived from observations | L0 + L1 (Blue + Gold) |
| **3** | **SIMULATED** | Theoretical/procedural content | L0 + L1 + L2 (All) |
| **H** | Help | Show keybinding reference | - |

---

## 🎨 Visual Guide

### Level 1: OBSERVED (Blue/White)
- **Visible:**
  - Earth's orbit around Sun (blue trail)
  - Gaia DR3 stars (white/blue points)
- **Hidden:**
  - Sun's galactic orbit (gold)
  - CMB velocity arrow (red)

### Level 2: INFERRED (Gold)
- **Visible:**
  - All OBSERVED layers
  - Sun's helical galactic path (gold trail)
  - Scale labels (oscillation amplitude)
- **Hidden:**
  - CMB velocity arrow (red)

### Level 3: SIMULATED (Red)
- **Visible:**
  - All layers (OBSERVED + INFERRED + SIMULATED)
  - CMB velocity vector arrow (red)

---

## 📁 File Structure

```
Epistemic-Engine/
├── src/
│   ├── db/
│   │   └── schema.sql              # Database schema
│   ├── ingestion/
│   │   ├── generate_sun_path.py    # Phase 1: Sun's orbit
│   │   ├── generate_cmb_arrow.py   # Phase 1: CMB arrow
│   │   ├── ingest_gaia.py          # Phase 2: Gaia ingestion
│   │   └── export_to_speck.py      # Phase 2: .speck export
│   └── assets/
│       ├── epistemic_engine_profile.asset  # Master profile
│       ├── intro_scene.asset       # Phase 1: Kinematics
│       ├── gaia_stars.asset        # Phase 2: Star rendering
│       └── ui/
│           ├── epistemic_dashboard.lua       # Phase 3: HUD
│           └── epistemic_keybindings.asset   # Phase 3: Controls
└── data/
    ├── sun_orbit/sun_galactic_orbit.csv
    ├── cmb_vector/cmb_velocity_arrow.obj
    └── gaia_observed.speck
```

---

## 🔬 Constitution Compliance

### ✅ Invariant I: Labeling (Provenance)
- Database enforces `truth_label NOT NULL`
- All objects tagged L0/L1/L2
- Provenance JSONB includes source DOI and error margins

###  ✅ Invariant II: Reference (Relative Motion)
- Earth → Sun (helix, not ellipse)
- Sun → Galaxy (oscillating wave)
- No absolute coordinates

### ✅ Invariant III: Access (Truth Slider)
- Persistent HUD shows active mode
- Keys 1/2/3 provide direct control
- Explicit layer toggling (no seamless blending)

---

## 🐛 Troubleshooting

### "Module not found: numpy"
```bash
pip3 install --user numpy
```

### "Database epistemic_engine does not exist"
```bash
createdb epistemic_engine
psql epistemic_engine < src/db/schema.sql
```

### "No module named 'astroquery'"
```bash
pip3 install --user astroquery astropy
```

### OpenSpace assets not loading
- Check file paths in `.asset` files
- Verify data files exist in `data/` directory
- Check OpenSpace console for Lua errors

---

## 📚 Documentation

- **Constitution**: `docs/Constitution.md` - The Three Invariants
- **Roadmap**: `docs/Roadmap.md` - 5-phase development plan
- **Architecture**: `docs/Architecture.md` - 4-plane system design
- **Contributor Guide**: `docs/Contributor_Guide.md` - Compliance checks
- **Database Setup**: `src/db/README.md` - PostgreSQL instructions
- **Keybindings**: `src/assets/ui/KEYBINDINGS.md` - Truth Slider controls

---

## 🎯 Next Steps

**Phase 4: The Gap (Laniakea)** - Coming Soon
- Generate Laniakea supercluster flow lines (L1 - INFERRED)
- Fill the "Empty Middle" with gravity field visualization
- Wiki system for focus-driven context panels

**Phase 5: Scale (Engineering)** - Future
- Binary octree optimization for 1 billion stars
- Level-of-detail (LOD) rendering
- Native OpenSpace format (OSP)

---

## 📜 License

*(To be determined)*

---

## 🙏 Acknowledgments

- **ESA Gaia Mission** - Precision stellar astrometry
- **NASA JPL Horizons** - Solar System ephemerides
- **Planck Collaboration** - CMB dipole measurements
- **OpenSpace Project** - Visualization framework

---

**"Show me the universe as it is, not as I wish it to be."**
