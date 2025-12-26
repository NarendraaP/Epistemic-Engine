# Database Schema

## Setup Instructions

### 1. Install PostgreSQL + PostGIS

**macOS (using Homebrew):**
```bash
brew install postgresql@15
brew install postgis
```

**Ubuntu/Debian:**
```bash
sudo apt-get install postgresql-15 postgresql-15-postgis-3
```

### 2. Create Database

```bash
# Start PostgreSQL service
brew services start postgresql@15  # macOS
# OR
sudo systemctl start postgresql    # Linux

# Create database
createdb epistemic_engine

# OR using psql
psql postgres
CREATE DATABASE epistemic_engine;
\q
```

### 3. Apply Schema

```bash
psql epistemic_engine < schema.sql
```

### 4. Verify Installation

```bash
psql epistemic_engine

# Inside psql:
\dx                          # List extensions (should show postgis)
\dT epistemic_status_type    # Show enum type
\d cosmic_objects            # Show table structure
\q
```

## Schema Overview

### Epistemic Status Enum
```sql
CREATE TYPE epistemic_status_type AS ENUM ('OBSERVED', 'INFERRED', 'SIMULATED');
```

### Cosmic Objects Table

| Column | Type | Constraints | Purpose |
|:-------|:-----|:------------|:--------|
| `id` | TEXT | PRIMARY KEY | Unique identifier (e.g., 'GaiaDR3_123456') |
| `truth_label` | epistemic_status_type | NOT NULL | **Invariant I**: Epistemic status |
| `location` | GEOGRAPHY(POINTZ) | - | **Invariant II**: Spherical 3D coords (RA/Dec/Distance) |
| `parallax_mas` | DOUBLE PRECISION | - | Parallax in milliarcseconds |
| `magnitude_g` | DOUBLE PRECISION | - | Gaia G-band magnitude |
| `color_index_bp_rp` | DOUBLE PRECISION | - | Color (BP-RP) |
| `provenance` | JSONB | NOT NULL | Source, DOI, error margins |
| `ingested_at` | TIMESTAMP | DEFAULT NOW() | Ingestion timestamp |

### Indexes

- **Spatial Index** (`idx_cosmic_location`): GIST index for fast cone searches
- **Epistemic Index** (`idx_cosmic_truth`): B-tree index for Truth Slider filtering

## Constitution Compliance

✅ **Invariant I (Labeling)**: `truth_label` column is NOT NULL  
✅ **Invariant II (Reference)**: Spherical coordinates (GEOGRAPHY)  
✅ **Invariant III (Access)**: Indexed for Truth Slider queries

## Sample Insert Statement

```sql
INSERT INTO cosmic_objects (
    id,
    truth_label,
    location,
    parallax_mas,
    magnitude_g,
    color_index_bp_rp,
    provenance
) VALUES (
    'GaiaDR3_4295806720',
    'OBSERVED',
    ST_GeographyFromText('POINTZ(83.633 -5.391 256.0)'),  -- RA, Dec, Distance(pc)
    3.9012,
    1.23,
    0.45,
    '{"source": "Gaia DR3", "doi": "10.1051/0004-6361/202243940", "parallax_error_mas": 0.023}'
);
```

## Query Examples

### Filter by Epistemic Status (Truth Slider)
```sql
-- Get only OBSERVED objects
SELECT id, magnitude_g FROM cosmic_objects WHERE truth_label = 'OBSERVED';
```

### Cone Search (Find stars near a position)
```sql
-- Find stars within 10 degrees of Betelgeuse (RA=88.79°, Dec=7.41°)
SELECT id, magnitude_g, ST_Distance(
    location,
    ST_GeographyFromText('POINT(88.79 7.41)')
) AS distance_degrees
FROM cosmic_objects
WHERE ST_DWithin(
    location,
    ST_GeographyFromText('POINT(88.79 7.41)'),
    10 * 111320  -- 10 degrees in meters (approx)
)
ORDER BY distance_degrees
LIMIT 100;
```

### Export to .speck format (via Python)
See `src/ingestion/export_to_speck.py`
