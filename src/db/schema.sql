-- ============================================================================
-- EPISTEMIC ENGINE - DATABASE SCHEMA
-- ============================================================================
-- Purpose: The Truth Store - Enforces Constitutional Invariants at DB level
-- Database: PostgreSQL 15+ with PostGIS extension
-- Coordinate System: ICRS (International Celestial Reference System)
--
-- CONSTITUTION COMPLIANCE:
-- - Invariant I (Labeling): truth_label column is NOT NULL
-- - Invariant II (Reference): GEOGRAPHY(POINTZ) for spherical coords
-- - Invariant III (Access): Indexed by truth_label for Truth Slider queries
-- ============================================================================

-- 1. ENABLE SPATIAL EXTENSIONS
CREATE EXTENSION IF NOT EXISTS postgis;

-- 2. DEFINE THE EPISTEMIC STATUS ENUM
-- This enforces the "Constitution" at the type level.
-- Only these 3 values are legally allowed in the database.
DO $$ BEGIN
    CREATE TYPE epistemic_status_type AS ENUM ('OBSERVED', 'INFERRED', 'SIMULATED');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- 3. CREATE THE TRUTH STORE TABLE
CREATE TABLE IF NOT EXISTS cosmic_objects (
    -- Unique Identifier (e.g., 'GaiaDR3_123456')
    id TEXT PRIMARY KEY,

    -- The "Truth Label" (Invariant of Labeling)
    -- NOT NULL constraint ensures no data enters without a label.
    truth_label epistemic_status_type NOT NULL,

    -- Spatial Position (Invariant of Reference)
    -- Using GEOGRAPHY(POINTZ) for spherical 3D coordinates (Long/Lat/Distance).
    -- SRID 4326 is standard WGS84, but we treat it as ICRS Celestial Sphere.
    location GEOGRAPHY(POINTZ, 4326),

    -- Physical Properties (Nullable, as not all objects have all props)
    parallax_mas DOUBLE PRECISION,     -- Measured Parallax
    magnitude_g DOUBLE PRECISION,      -- Apparent Magnitude
    color_index_bp_rp DOUBLE PRECISION, -- Star Color (Blue/Red Photometer)

    -- Provenance Metadata (The "Why")
    -- Stores Source, DOI, and Error Margins.
    provenance JSONB NOT NULL,

    -- Housekeeping
    ingested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 4. CREATE INDEXES FOR PERFORMANCE
-- Spatial Index for Cone Searches (Crucial for Octree generation later)
CREATE INDEX IF NOT EXISTS idx_cosmic_location ON cosmic_objects USING GIST (location);

-- Epistemic Index for "Truth Slider" Filtering
CREATE INDEX IF NOT EXISTS idx_cosmic_truth ON cosmic_objects (truth_label);

-- 5. VERIFICATION COMMENT
COMMENT ON TABLE cosmic_objects IS 'The Truth Store: Enforces Epistemic Invariants on all celestial data.';
