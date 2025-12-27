"""
Ingestion Module

Data processing pipelines for converting astronomical data into epistemic-labeled formats.

Modules:
    - ingest_gaia: Gaia DR3 catalog ingestion
    - generate_laniakea: Laniakea supercluster structure
    - generate_sun_path: Sun's galactic orbit
    - generate_cmb_arrow: CMB velocity vector
    - export_to_speck: OpenSpace .speck format exporter
    - export_binary_octree: Binary octree for massive catalogs
"""

__all__ = [
    "ingest_gaia",
    "generate_laniakea",
    "generate_sun_path",
    "generate_cmb_arrow",
    "export_to_speck",
    "export_binary_octree",
]
