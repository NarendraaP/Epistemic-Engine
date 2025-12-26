"""
Epistemic Engine - Database Schema Tests
=========================================

PURPOSE: Validate PostgreSQL schema compliance with Constitution

Tests ensure:
1. Schema file contains required epistemic_status_type enum
2. NOT NULL constraints are present
3. Database structure enforces all invariants
"""

import pytest
import re
from pathlib import Path


# =============================================================================
# SCHEMA FILE TESTS
# =============================================================================

class TestDatabaseSchema:
    """Test that database schema enforces Constitutional requirements."""
    
    @pytest.fixture
    def schema_content(self):
        """Load schema.sql file content."""
        schema_path = Path('src/db/schema.sql')
        
        if not schema_path.exists():
            pytest.skip("schema.sql not found")
        
        with open(schema_path, 'r') as f:
            return f.read()
    
    def test_epistemic_status_enum_exists(self, schema_content):
        """
        Test that schema defines epistemic_status_type enum.
        
        Constitution: "Database must enforce epistemic labeling at type level"
        
        Expected pattern:
            CREATE TYPE epistemic_status_type AS ENUM (...)
        """
        pattern = r'CREATE\s+TYPE\s+epistemic_status_type\s+AS\s+ENUM'
        
        assert re.search(pattern, schema_content, re.IGNORECASE), \
            "Schema must define epistemic_status_type AS ENUM"
    
    def test_enum_values_correct(self, schema_content):
        """
        Test that enum contains exactly OBSERVED, INFERRED, SIMULATED.
        
        Constitution: "Only these three values are legally allowed"
        """
        # Find enum definition
        pattern = r"CREATE\s+TYPE\s+epistemic_status_type\s+AS\s+ENUM\s*\((.*?)\)"
        match = re.search(pattern, schema_content, re.IGNORECASE | re.DOTALL)
        
        assert match, "Could not find enum definition"
        
        enum_values = match.group(1)
        
        # Check for required values
        assert "'OBSERVED'" in enum_values or '"OBSERVED"' in enum_values, \
            "Enum must include 'OBSERVED'"
        assert "'INFERRED'" in enum_values or '"INFERRED"' in enum_values, \
            "Enum must include 'INFERRED'"
        assert "'SIMULATED'" in enum_values or '"SIMULATED"' in enum_values, \
            "Enum must include 'SIMULATED'"
    
    def test_cosmic_objects_table_exists(self, schema_content):
        """Test that cosmic_objects table is defined."""
        pattern = r'CREATE\s+TABLE.*cosmic_objects'
        
        assert re.search(pattern, schema_content, re.IGNORECASE | re.DOTALL), \
            "Schema must define cosmic_objects table"
    
    def test_truth_label_not_null(self, schema_content):
        """
        Test that truth_label column has NOT NULL constraint.
        
        Constitution Invariant I: "truth_label column is NOT NULL"
        """
        # Find truth_label column definition
        # Pattern: truth_label ... NOT NULL
        pattern = r'truth_label\s+\w+\s+NOT\s+NULL'
        
        assert re.search(pattern, schema_content, re.IGNORECASE), \
            "truth_label must have NOT NULL constraint"
    
    def test_provenance_not_null(self, schema_content):
        """
        Test that provenance column has NOT NULL constraint.
        
        Constitution: "Provenance JSONB NOT NULL"
        """
        pattern = r'provenance\s+JSONB\s+NOT\s+NULL'
        
        assert re.search(pattern, schema_content, re.IGNORECASE), \
            "provenance must be JSONB NOT NULL"
    
    def test_location_geography_type(self, schema_content):
        """
        Test that location uses GEOGRAPHY type (not GEOMETRY).
        
        Constitution Invariant II: Spherical coordinates (GEOGRAPHY)
        """
        # Pattern: location GEOGRAPHY(POINTZ, ...)
        pattern = r'location\s+GEOGRAPHY\s*\(\s*POINTZ'
        
        assert re.search(pattern, schema_content, re.IGNORECASE), \
            "location must use GEOGRAPHY(POINTZ) for spherical coords"
    
    def test_epistemic_index_exists(self, schema_content):
        """
        Test that index on truth_label exists for Truth Slider queries.
        
        Constitution Invariant III: Indexed for filtering
        """
        # Pattern: CREATE INDEX ... ON cosmic_objects (truth_label)
        pattern = r'CREATE\s+INDEX.*ON\s+cosmic_objects\s*\(\s*truth_label\s*\)'
        
        assert re.search(pattern, schema_content, re.IGNORECASE | re.DOTALL), \
            "Must have index on truth_label for Truth Slider performance"
    
    def test_spatial_index_exists(self, schema_content):
        """Test that spatial index (GIST) exists on location."""
        pattern = r'CREATE\s+INDEX.*USING\s+GIST\s*\(\s*location\s*\)'
        
        assert re.search(pattern, schema_content, re.IGNORECASE | re.DOTALL), \
            "Must have GIST index on location for spatial queries"
    
    def test_postgis_extension_enabled(self, schema_content):
        """Test that PostGIS extension is enabled."""
        pattern = r'CREATE\s+EXTENSION.*postgis'
        
        assert re.search(pattern, schema_content, re.IGNORECASE), \
            "Must enable PostGIS extension"


# =============================================================================
# SCHEMA SEMANTIC TESTS
# =============================================================================

class TestSchemaSemantics:
    """Test semantic correctness of schema design."""
    
    @pytest.fixture
    def schema_content(self):
        """Load schema.sql file content."""
        schema_path = Path('src/db/schema.sql')
        
        if not schema_path.exists():
            pytest.skip("schema.sql not found")
        
        with open(schema_path, 'r') as f:
            return f.read()
    
    def test_no_absolute_coordinates_column(self, schema_content):
        """
        Test that schema does not have 'absolute_*' coordinate columns.
        
        Constitution Invariant II: "Absolute coordinates are forbidden"
        """
        # Check for suspicious column names
        forbidden_patterns = [
            r'\babsolute_position\b',
            r'\babsolute_x\b',
            r'\babsolute_y\b',
            r'\babsolute_z\b'
        ]
        
        for pattern in forbidden_patterns:
            assert not re.search(pattern, schema_content, re.IGNORECASE), \
                f"Schema must not contain absolute coordinate columns: {pattern}"
    
    def test_parallax_column_exists(self, schema_content):
        """
        Test that parallax column exists (for distance calculation).
        
        Parallax is the OBSERVED quantity; distance is INFERRED from it.
        """
        pattern = r'\bparallax'
        
        assert re.search(pattern, schema_content, re.IGNORECASE), \
            "Schema should store parallax (observed quantity)"
    
    def test_magnitude_column_exists(self, schema_content):
        """Test that magnitude column exists (for brightness queries)."""
        pattern = r'\bmagnitude'
        
        assert re.search(pattern, schema_content, re.IGNORECASE), \
            "Schema should store magnitude for brightness filtering"
    
    def test_comment_on_table(self, schema_content):
        """Test that table has explanatory comment."""
        pattern = r'COMMENT\s+ON\s+TABLE\s+cosmic_objects'
        
        assert re.search(pattern, schema_content, re.IGNORECASE), \
            "Table should have descriptive comment"


# =============================================================================
# SCHEMA VALIDATION AGAINST CONSTITUTION
# =============================================================================

class TestConstitutionalCompliance:
    """High-level validation against Constitutional requirements."""
    
    @pytest.fixture
    def schema_content(self):
        """Load schema.sql file content."""
        schema_path = Path('src/db/schema.sql')
        
        if not schema_path.exists():
            pytest.skip("schema.sql not found")
        
        with open(schema_path, 'r') as f:
            return f.read()
    
    def test_all_invariants_enforced(self, schema_content):
        """
        Comprehensive test that all three invariants are present.
        
        Invariant I: truth_label NOT NULL + epistemic_status_type enum
        Invariant II: GEOGRAPHY(POINTZ) for spherical coords
        Invariant III: Index on truth_label
        """
        # Check Invariant I
        assert 'epistemic_status_type' in schema_content, "Missing Invariant I (enum)"
        assert re.search(r'truth_label.*NOT\s+NULL', schema_content, re.IGNORECASE), \
            "Missing Invariant I (NOT NULL)"
        
        # Check Invariant II
        assert 'GEOGRAPHY' in schema_content, "Missing Invariant II (GEOGRAPHY type)"
        assert 'POINTZ' in schema_content, "Missing Invariant II (POINTZ for 3D)"
        
        # Check Invariant III
        assert re.search(r'INDEX.*truth_label', schema_content, re.IGNORECASE), \
            "Missing Invariant III (truth_label index)"
    
    def test_schema_has_version_or_date(self, schema_content):
        """Test that schema includes version info or date in comments."""
        # Look for common version/date patterns in comments
        has_version_info = (
            re.search(r'--.*version', schema_content, re.IGNORECASE) or
            re.search(r'--.*\d{4}-\d{2}-\d{2}', schema_content) or  # Date: YYYY-MM-DD
            re.search(r'/\*.*version', schema_content, re.IGNORECASE)
        )
        
        # This is a good practice but not strictly required
        # So we just warn if missing
        if not has_version_info:
            pytest.warns(UserWarning, match="Schema should include version/date")


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
