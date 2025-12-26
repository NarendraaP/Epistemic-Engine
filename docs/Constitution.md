# 📜 The Epistemic Constitution (v1.0)
**Status:** Ratified | **Date:** Dec 2025

## 1. The Core Mandate
The goal of this engine is not realism; it is **Epistemic Clarity**. 
We visualize the universe as a hierarchy of certainty, distinguishing between what is measured, what is inferred, and what is simulated.

## 2. The Three Invariants (The "Musts")

### I. The Invariant of Labeling (Provenance)
> **Rule:** No object shall appear on screen without an explicit `Epistemic_Status`.
* **Constraint:** All database rows MUST have a `truth_label` column.
* **Allowed Values:** `OBSERVED`, `INFERRED`, `SIMULATED`.
* **Null Policy:** Rows with NULL labels are rejected at ingestion.

### II. The Invariant of Reference (Relative Motion)
> **Rule:** Motion must be visualized relative to its parent frame.
* **Earth** moves relative to **Sun** (Result: Helix/Corkscrew).
* **Sun** moves relative to **Galactic Center** (Result: Wave/Oscillation).
* **Galaxy** moves relative to **CMB** (Result: Velocity Vector).
* **Forbidden:** "Absolute" coordinates that hide these nested relationships.

### III. The Invariant of Access (User Interface)
> **Rule:** The "Truth Slider" must be the primary navigation control.
* **Constraint:** A persistent On-Screen Display (OSD) or Dashboard must indicate the current epistemic filter mode at all times.

## 3. The Layer Definition

| Layer ID | Name | Color Code | Definition | Allowed Data Sources |
| :--- | :--- | :--- | :--- | :--- |
| **L0** | **OBSERVED** | **White / Blue** | Direct Measurement | Gaia, Hipparcos, JPL Ephemerides (SPICE), SDSS Spectroscopy |
| **L1** | **INFERRED** | **Gold / Yellow** | Derived from Model | Cosmicflows (Gravity Fields), Orbit Models (Oscillation), Rotation Curves |
| **L2** | **SIMULATED** | **Red / Amber** | Procedural / Theoretical | IllustrisTNG, Procedural Exoplanet Terrain, Hypothetical fill |

## 4. The "Empty Middle" Policy
* **Rule:** We acknowledge the visual gap between Stars (Micro) and the CMB (Macro).
* **Constraint:** We fill it **only** with `INFERRED` data (e.g., Laniakea flow lines), never with procedural decoration just to avoid emptiness.
