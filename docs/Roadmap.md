# 🗺️ Project Roadmap (v1.0)

## ✅ Phase 1: The Anchor (Kinematics)
**Goal:** Establish the nested coordinate system so the user understands motion.
* [x] **Python:** Generate Sun's Galactic Path (Inferred Wave).
    * *Math:* Helical sine wave (Period=230Myr, Oscillation=60Myr).
* [x] **Python:** Generate CMB Vector (Inferred Arrow).
* [x] **OpenSpace:** Intro Scene asset with anchored Reference Frames.
* [x] **UI:** Anchored Labels (e.g., "Vertical Oscillation ≈ 70pc").

## 🔄 Phase 2: The Truth (Gaia Ingestion)
**Goal:** Ingest the "Observed" layer with provenance.
* [ ] **SQL:** Create `cosmic_objects` table with `truth_label` Enum.
* [ ] **Python:** Ingest Gaia DR3 subset (Bright Stars) into PostGIS.
* [ ] **Python:** Export `gaia_observed.speck` (Chunked Text).
* [ ] **OpenSpace:** Render `OBSERVED` layer (White/Blue) mapped to magnitude.

## ⏳ Phase 3: The Interaction (UX)
**Goal:** Give user control over the Truth Levels.
* [ ] **Lua:** Build the Dashboard HUD (Screen-space text).
* [ ] **Lua:** Implement Truth Slider logic (Toggle Layers 1, 2, 3).
* [ ] **Config:** Bind keys (1, 2, 3) to the slider states.

## ⏳ Phase 4: The Gap (Laniakea)
**Goal:** Fill the "Empty Middle".
* [ ] **Python:** Generate Laniakea Flow Lines and Galaxies (`INFERRED`).
* [ ] **OpenSpace:** Render Structure as Gold lines.
* [ ] **Lua:** Wiki System (Focus-driven context panel).

## 🔮 Phase 5: Scale (Engineering)
**Goal:** 1 Billion Stars (Only after UX is proven).
* [ ] **C++:** Binary Octree Implementation or Native OSP format.
