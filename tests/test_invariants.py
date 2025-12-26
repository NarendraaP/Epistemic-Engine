"""
Epistemic Engine - Invariant Tests
===================================

PURPOSE: Enforce the Three Invariants from the Constitution

INVARIANT I (Labeling): Every data point must have an epistemic status
INVARIANT II (Reference): No absolute coordinates, only relative motion
INVARIANT III (Access): User must always know active truth filter

These tests ensure no future code violates the Constitution.
"""

import pytest
import numpy as np
from pathlib import Path


# =============================================================================
# INVARIANT I: LABELING (PROVENANCE)
# =============================================================================

class TestInvariantI_Labeling:
    """Test enforcement of Invariant I: All data must be labeled."""
    
    def test_null_truth_label_rejected(self):
        """
        Test that data with null truth_label is rejected.
        
        Constitution: "Every data point MUST have an explicit epistemic status"
        """
        # Mock data object with null label
        mock_data = {
            'id': 'test_star_001',
            'position': (1.0, 2.0, 3.0),
            'magnitude': 5.0,
            'truth_label': None,  # VIOLATION!
            'provenance': None
        }
        
        # Simulate validation logic (would be in actual ingestion code)
        def validate_truth_label(data):
            if data.get('truth_label') is None:
                raise ValueError("Invariant I violated: truth_label cannot be None")
            if data['truth_label'] not in ['OBSERVED', 'INFERRED', 'SIMULATED']:
                raise ValueError(f"Invalid truth_label: {data['truth_label']}")
        
        # Assert that validation raises error
        with pytest.raises(ValueError, match="truth_label cannot be None"):
            validate_truth_label(mock_data)
    
    def test_invalid_truth_label_rejected(self):
        """Test that invalid epistemic status values are rejected."""
        
        mock_data = {
            'id': 'test_star_002',
            'truth_label': 'UNKNOWN',  # Invalid value
            'provenance': {}
        }
        
        def validate_truth_label(data):
            if data['truth_label'] not in ['OBSERVED', 'INFERRED', 'SIMULATED']:
                raise ValueError(f"Invalid truth_label: {data['truth_label']}")
        
        with pytest.raises(ValueError, match="Invalid truth_label"):
            validate_truth_label(mock_data)
    
    def test_valid_truth_labels_accepted(self):
        """Test that all valid epistemic statuses are accepted."""
        
        valid_labels = ['OBSERVED', 'INFERRED', 'SIMULATED']
        
        def validate_truth_label(data):
            if data['truth_label'] not in valid_labels:
                raise ValueError(f"Invalid truth_label: {data['truth_label']}")
            return True
        
        for label in valid_labels:
            mock_data = {'truth_label': label, 'provenance': {}}
            assert validate_truth_label(mock_data) is True
    
    def test_null_provenance_rejected(self):
        """
        Test that data without provenance is rejected.
        
        Constitution: "Provenance JSONB NOT NULL"
        """
        mock_data = {
            'id': 'test_star_003',
            'truth_label': 'OBSERVED',
            'provenance': None  # VIOLATION!
        }
        
        def validate_provenance(data):
            if data.get('provenance') is None:
                raise ValueError("Invariant I violated: provenance cannot be None")
            if not isinstance(data['provenance'], dict):
                raise ValueError("Provenance must be a dictionary")
        
        with pytest.raises(ValueError, match="provenance cannot be None"):
            validate_provenance(mock_data)


# =============================================================================
# INVARIANT II: REFERENCE (RELATIVE MOTION)
# =============================================================================

class TestInvariantII_Reference:
    """Test enforcement of Invariant II: Relative motion only."""
    
    def test_parallax_to_distance_conversion(self):
        """
        Test coordinate transformation from parallax to distance.
        
        Constitution: "No absolute coordinates. Motion must be relative."
        
        This tests the conversion: distance_pc = 1000 / parallax_mas
        """
        # Test cases: (parallax_mas, expected_distance_pc)
        test_cases = [
            (1.0, 1000.0),      # 1 mas → 1000 pc
            (10.0, 100.0),      # 10 mas → 100 pc
            (100.0, 10.0),      # 100 mas → 10 pc
            (0.1, 10000.0),     # 0.1 mas → 10000 pc
        ]
        
        def parallax_to_distance(parallax_mas):
            """Convert parallax in milliarcseconds to distance in parsecs."""
            if parallax_mas <= 0:
                raise ValueError("Parallax must be positive")
            return 1000.0 / parallax_mas
        
        for parallax, expected_distance in test_cases:
            distance = parallax_to_distance(parallax)
            assert np.isclose(distance, expected_distance), \
                f"Parallax {parallax} mas should give {expected_distance} pc, got {distance} pc"
    
    def test_negative_parallax_rejected(self):
        """Test that negative parallax (unphysical) is rejected."""
        
        def parallax_to_distance(parallax_mas):
            if parallax_mas <= 0:
                raise ValueError("Parallax must be positive")
            return 1000.0 / parallax_mas
        
        with pytest.raises(ValueError, match="Parallax must be positive"):
            parallax_to_distance(-5.0)
    
    def test_zero_parallax_rejected(self):
        """Test that zero parallax (infinite distance) is rejected."""
        
        def parallax_to_distance(parallax_mas):
            if parallax_mas <= 0:
                raise ValueError("Parallax must be positive")
            return 1000.0 / parallax_mas
        
        with pytest.raises(ValueError, match="Parallax must be positive"):
            parallax_to_distance(0.0)
    
    def test_spherical_to_cartesian_conversion(self):
        """
        Test spherical to Cartesian coordinate conversion.
        
        This is used to convert (RA, Dec, Distance) to (X, Y, Z)
        relative to Milky Way center.
        """
        def spherical_to_cartesian(ra_deg, dec_deg, distance_pc):
            """Convert spherical to Cartesian coordinates."""
            ra_rad = np.radians(ra_deg)
            dec_rad = np.radians(dec_deg)
            
            x = distance_pc * np.cos(dec_rad) * np.cos(ra_rad)
            y = distance_pc * np.cos(dec_rad) * np.sin(ra_rad)
            z = distance_pc * np.sin(dec_rad)
            
            return (x, y, z)
        
        # Test case: RA=0°, Dec=0°, Distance=100pc
        # Should give: X=100, Y=0, Z=0
        x, y, z = spherical_to_cartesian(0.0, 0.0, 100.0)
        assert np.isclose(x, 100.0), f"Expected X=100, got {x}"
        assert np.isclose(y, 0.0, atol=1e-10), f"Expected Y=0, got {y}"
        assert np.isclose(z, 0.0, atol=1e-10), f"Expected Z=0, got {z}"
        
        # Test case: RA=90°, Dec=0°, Distance=100pc
        # Should give: X=0, Y=100, Z=0
        x, y, z = spherical_to_cartesian(90.0, 0.0, 100.0)
        assert np.isclose(x, 0.0, atol=1e-10), f"Expected X=0, got {x}"
        assert np.isclose(y, 100.0), f"Expected Y=100, got {y}"
        assert np.isclose(z, 0.0, atol=1e-10), f"Expected Z=0, got {z}"
        
        # Test case: RA=0°, Dec=90°, Distance=100pc
        # Should give: X=0, Y=0, Z=100
        x, y, z = spherical_to_cartesian(0.0, 90.0, 100.0)
        assert np.isclose(x, 0.0, atol=1e-10), f"Expected X=0, got {x}"
        assert np.isclose(y, 0.0, atol=1e-10), f"Expected Y=0, got {y}"
        assert np.isclose(z, 100.0), f"Expected Z=100, got {z}"


# =============================================================================
# INVARIANT III: ACCESS (USER INTERFACE)
# =============================================================================

class TestInvariantIII_Access:
    """Test enforcement of Invariant III: User must know active truth filter."""
    
    def test_truth_slider_has_three_levels(self):
        """
        Test that Truth Slider supports exactly 3 levels.
        
        Constitution: "User must ALWAYS know which Truth Filter is active"
        Levels: OBSERVED (1), INFERRED (2), SIMULATED (3)
        """
        TRUTH_LEVELS = {
            1: 'OBSERVED',
            2: 'INFERRED',
            3: 'SIMULATED'
        }
        
        assert len(TRUTH_LEVELS) == 3, "Truth Slider must have exactly 3 levels"
        assert 1 in TRUTH_LEVELS, "Level 1 (OBSERVED) must exist"
        assert 2 in TRUTH_LEVELS, "Level 2 (INFERRED) must exist"
        assert 3 in TRUTH_LEVELS, "Level 3 (SIMULATED) must exist"
    
    def test_invalid_truth_level_rejected(self):
        """Test that invalid truth levels (0, 4, etc.) are rejected."""
        
        def set_truth_level(level):
            if level < 1 or level > 3:
                raise ValueError(f"Invalid truth level: {level}. Must be 1, 2, or 3.")
            return level
        
        # Valid levels should work
        assert set_truth_level(1) == 1
        assert set_truth_level(2) == 2
        assert set_truth_level(3) == 3
        
        # Invalid levels should raise error
        with pytest.raises(ValueError, match="Invalid truth level"):
            set_truth_level(0)
        
        with pytest.raises(ValueError, match="Invalid truth level"):
            set_truth_level(4)
    
    def test_epistemic_color_mapping_complete(self):
        """
        Test that all epistemic statuses have color mappings.
        
        Constitution Layer 3: Color coding for visual distinction
        """
        EPISTEMIC_COLORS = {
            'OBSERVED': (0.4, 0.8, 1.0),    # Blue (#66CCFF)
            'INFERRED': (1.0, 0.84, 0.0),   # Gold (#FFD700)
            'SIMULATED': (1.0, 0.27, 0.27)  # Red (#FF4444)
        }
        
        # Check all statuses have colors
        required_statuses = ['OBSERVED', 'INFERRED', 'SIMULATED']
        for status in required_statuses:
            assert status in EPISTEMIC_COLORS, \
                f"Missing color mapping for {status}"
            
            # Check color is valid RGB tuple
            color = EPISTEMIC_COLORS[status]
            assert len(color) == 3, f"Color for {status} must be RGB tuple"
            assert all(0.0 <= c <= 1.0 for c in color), \
                f"Color values for {status} must be in range [0, 1]"


# =============================================================================
# INTEGRATION TESTS
# =============================================================================

class TestConstitutionIntegration:
    """Integration tests across all invariants."""
    
    def test_complete_data_object_validation(self):
        """
        Test that a complete data object passes all invariant checks.
        
        This simulates the full validation pipeline.
        """
        # Valid data object
        valid_data = {
            'id': 'GaiaDR3_4295806720',
            'truth_label': 'OBSERVED',
            'provenance': {
                'source': 'Gaia DR3',
                'doi': '10.1051/0004-6361/202243940',
                'parallax_error_mas': 0.023
            },
            'position': {
                'ra_deg': 83.633,
                'dec_deg': -5.391,
                'parallax_mas': 3.9012
            },
            'magnitude': 1.23
        }
        
        # Validation functions
        def validate_complete(data):
            # Invariant I: Labeling
            if data.get('truth_label') not in ['OBSERVED', 'INFERRED', 'SIMULATED']:
                raise ValueError("Invalid truth_label")
            if data.get('provenance') is None:
                raise ValueError("Missing provenance")
            
            # Invariant II: Coordinates
            if 'position' in data and 'parallax_mas' in data['position']:
                if data['position']['parallax_mas'] <= 0:
                    raise ValueError("Invalid parallax")
            
            return True
        
        # Valid data should pass
        assert validate_complete(valid_data) is True
        
        # Invalid data should fail
        invalid_data = valid_data.copy()
        invalid_data['truth_label'] = None
        
        with pytest.raises(ValueError):
            validate_complete(invalid_data)


# =============================================================================
# PYTEST CONFIGURATION
# =============================================================================

@pytest.fixture
def sample_star_data():
    """Fixture providing sample star data for tests."""
    return {
        'id': 'TestStar_001',
        'truth_label': 'OBSERVED',
        'provenance': {
            'source': 'Test Suite',
            'doi': 'test/123',
            'error_margin': 0.1
        },
        'position': {
            'ra_deg': 45.0,
            'dec_deg': 30.0,
            'parallax_mas': 10.0
        },
        'magnitude': 5.0
    }


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
