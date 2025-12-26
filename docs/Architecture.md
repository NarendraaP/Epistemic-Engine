# 🏗️ Technical Architecture

## 1. The Data Plane (The Truth Store)
* **Database:** PostGIS (PostgreSQL + GIS Extension).
* **Coordinate System:** ICRS (Spherical).
* **Schema:**
  * `id` (Primary Key)
  * `location` (Geography Point)
  * `epistemic_status` (Enum: OBSERVED, INFERRED, SIMULATED)
  * `provenance` (JSONB: DOI, Source, Error Margin)

## 2. The Ingestion Plane (The Adjudicator)
* **Language:** Python 3.10+.
* **Libraries:** `astroquery` (ESA/Gaia), `psycopg2` (DB), `numpy` (Math).
* **Role:** Queries external APIs, adjudicates the Truth Label based on error margins, inserts into DB.

## 3. The Transport Plane (The Bridge)
* **Format (v1):** Chunked `.speck` files (Text-based).
  * *Reasoning:* Human-readable, easy to debug, native to OpenSpace.
* **Format (v2):** Binary Octree / OSP (Future optimization).
* **Logic:** Pre-generation via Python scripts; no runtime SQL queries in v1 for performance safety.

## 4. The Render Plane (The Viewer)
* **Engine:** OpenSpace (Reference Implementation).
* **Scripting:** Lua.
* **Assets:** Custom `.asset` files linking Geometries, Scripts, and Keybindings.
