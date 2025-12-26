# The Epistemic Engine (v1.0)

> **"To visualize the universe not as a photograph, but as a hierarchy of certainty."**

## 🔭 What is this?
This is a scientific visualization standard and rendering pipeline designed to fix the "Epistemic Gap" in modern astronomy education. It rigorously distinguishes between:
1.  **OBSERVED (White):** What we see (Gaia Stars).
2.  **INFERRED (Gold):** What we model (Gravity Flows, Orbits).
3.  **SIMULATED (Red):** What we guess (Procedural fills).

## 🏗️ Architecture
* **Truth Store:** PostGIS database enforcing provenance.
* **Adjudicator:** Python pipelines that reject unlabeled data.
* **Viewer:** OpenSpace (Lua-scripted) with a custom "Truth Slider" HUD.

## 🚀 Quick Start

**Option 1: One-Click Build (Recommended)**
```bash
# Generate all data files (no database required)
python3 run_pipeline.py

# Or run specific phases only
python3 run_pipeline.py --phases 1,4
```

**Option 2: Manual Steps**
1.  **Initialize DB:** Run `src/db/schema.sql` (optional).
2.  **Generate Data:** Run individual scripts in `src/ingestion/`.
3.  **Launch:** Open `epistemic_engine_profile.asset` in OpenSpace.
4.  **Interact:** Use Keys `1-2-3` to toggle Truth Levels.

## ⚖️ Governance
This project adheres to the **Epistemic Constitution** (`docs/Constitution.md`).
Absolute coordinates and unlabeled data are strictly forbidden.

---

## 📚 Documentation

### Core Documents
- **[Constitution](docs/Constitution.md)** - The Three Invariants (Labeling, Reference, Access)
- **[Roadmap](docs/Roadmap.md)** - 5-phase development plan (ALL PHASES COMPLETE ✅)
- **[Architecture](docs/Architecture.md)** - 4-plane system design
- **[Contributor Guide](docs/Contributor_Guide.md)** - Compliance checks before commit

### Phase Documentation
- **[Phase 5: Scale Engineering](docs/Phase5_Scale_Engineering.md)** - Binary octree system for massive catalogs
- **[Quick Start Guide](QUICKSTART.md)** - Installation and usage
- **[Keybindings](src/assets/ui/KEYBINDINGS.md)** - Truth Slider controls

---

## 🎮 Truth Slider Controls

| Key | Mode | Description | Visible Layers |
|:---:|:-----|:------------|:---------------|
| **1** | **OBSERVED** | Direct measurements with error bars | Earth orbit + Gaia stars (Blue/White) |
| **2** | **INFERRED** | Models derived from observations | + Sun's orbit + Laniakea (Gold) |
| **3** | **SIMULATED** | Theoretical/procedural content | + CMB arrow (Red) |
| **H** | Help | Show keybinding reference | - |

---

## 📦 What's Included

### Phase 1: The Anchor (Kinematics) ✅
- Sun's helical galactic orbit (230 Myr period, L1 - INFERRED)
- CMB velocity vector (369 km/s towards Leo, L2 - SIMULATED)
- Nested coordinate system: Earth → Sun → Galaxy → CMB

### Phase 2: The Truth (Gaia Ingestion) ✅
- PostgreSQL schema with `epistemic_status_type` enum
- Gaia DR3 ingestion pipeline (rejects stars without error margins)
- Export to OpenSpace `.speck` format
- 100,000 brightest stars rendered (L0 - OBSERVED)

### Phase 3: The Interaction (UX) ✅
- Epistemic dashboard HUD (always-visible mode indicator)
- Truth Slider keybindings (1/2/3)
- Explicit layer toggling (no seamless blending)

### Phase 4: The Gap (Laniakea) ✅
- Laniakea supercluster structure (~5,000 galaxies, L1 - INFERRED)
- Cosmic web filaments and flow vectors
- Fills "Empty Middle" per Constitution policy
- Based on Tully et al. 2014 (DOI: 10.1038/nature13674)

### Phase 5: Scale (Engineering) ✅
- Binary octree export system for millions of stars
- LOD (Level of Detail) manager framework
- Parent nodes: brightest 10%, Children: full detail
- Conceptual framework (requires C++ for production)

---

## 🛠️ Technology Stack

**Database:**
- PostgreSQL 15+ with PostGIS
- Custom `epistemic_status_type` enum
- JSONB provenance metadata

**Backend:**
- Python 3.7+
- Libraries: `numpy`, `psycopg2-binary`, `astroquery`, `astropy`

**Visualization:**
- OpenSpace 0.19+
- Lua scripting for assets and UI
- Custom Truth Slider dashboard

**Data Sources:**
- Gaia DR3 (ESA mission)
- NASA JPL Horizons (SPICE)
- Planck 2018 CMB measurements
- Cosmicflows-2 (Laniakea)

---

## 🌌 Scale Coverage

The Epistemic Engine visualizes **13 orders of magnitude** of spatial scale:

| Scale | Object | Distance | Epistemic Status |
|:------|:-------|:---------|:-----------------|
| **10⁸ m** | Earth orbit | 1 AU | L0 (OBSERVED) |
| **10¹⁶ m** | Nearby stars | ~10 pc | L0 (OBSERVED) |
| **10²⁰ m** | Sun's orbit | ~8.5 kpc | L1 (INFERRED) |
| **10²³ m** | Laniakea | ~160 Mpc | L1 (INFERRED) |
| **10²⁶ m** | Observable universe | ~46 Gpc | (Future) |

---

## ⚖️ The Three Invariants

### I. Invariant of Labeling (Provenance)
**Rule:** Every data point must have an explicit epistemic status and source.

**Database Enforcement:**
```sql
CREATE TABLE cosmic_objects (
    truth_label epistemic_status_type NOT NULL,  -- Enum: OBSERVED/INFERRED/SIMULATED
    provenance JSONB NOT NULL                    -- Source DOI + error margins
);
```

### II. Invariant of Reference (Relative Motion)
**Rule:** Motion must be relative to parent frames. No absolute coordinates.

**Scene Graph:**
```
CMB (root)
└── GalacticCenter
    └── SunInGalaxy
        └── EarthInSolarSystem
```

### III. Invariant of Access (User Interface)
**Rule:** User must ALWAYS know which Truth Filter is active.

**Implementation:**
- Persistent HUD showing epistemic mode
- Keybindings for direct control (1/2/3)
- Explicit layer toggling (no gradual blending)

---

## 🚧 Roadmap Status

- [x] **Phase 1:** The Anchor (Kinematics)
- [x] **Phase 2:** The Truth (Gaia Ingestion)
- [x] **Phase 3:** The Interaction (UX)
- [x] **Phase 4:** The Gap (Laniakea)
- [x] **Phase 5:** Scale (Engineering)

**All 5 phases complete!** 🎉

**Future work:**
- C++ binary point cloud renderer for production
- Full Gaia DR3 catalog (1.8 billion stars)
- Streaming from database (no pre-export)

---

## 📜 License

*(To be determined)*

---

## 🙏 Acknowledgments

- **ESA Gaia Mission** - Precision stellar astrometry
- **NASA JPL Horizons** - Solar System ephemerides
- **Planck Collaboration** - CMB dipole measurements
- **R. Brent Tully et al.** - Laniakea supercluster discovery
- **OpenSpace Project** - Visualization framework

---

## 📧 Contact

*(To be added)*

---

**"Show me the universe as it is, not as I wish it to be."**
