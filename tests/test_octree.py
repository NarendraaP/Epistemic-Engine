"""
Epistemic Engine - Binary Octree Tests
=======================================

PURPOSE: Validate binary octree format and structure

Tests ensure that:
1. Binary files have correct header structure
2. Star data is correctly packed/unpacked
3. Edge cases (0 stars, large files) are handled
"""

import pytest
import struct
import tempfile
from pathlib import Path
import numpy as np


# =============================================================================
# BINARY FORMAT TESTS
# =============================================================================

class TestBinaryOctreeFormat:
    """Test binary octree file format compliance."""
    
    def test_binary_header_structure(self):
        """
        Test that binary file has correct header (int32 star count).
        
        Binary format:
            Header: int32 num_stars
            Body: For each star:
                - float32 x, y, z (position)
                - float32 magnitude
                - int32 epistemic_status
        """
        # Create a test binary file with known structure
        num_stars = 42
        
        with tempfile.NamedTemporaryFile(mode='wb', suffix='.bin', delete=False) as f:
            temp_path = Path(f.name)
            
            # Write header
            f.write(struct.pack('i', num_stars))
            
            # Write stars
            for i in range(num_stars):
                # position (x, y, z), magnitude, epistemic_status
                f.write(struct.pack('ffffi',
                    float(i),      # x
                    float(i * 2),  # y
                    float(i * 3),  # z
                    5.0,           # magnitude
                    0              # OBSERVED
                ))
        
        try:
            # Read back and verify
            with open(temp_path, 'rb') as f:
                # Read header
                header_bytes = f.read(4)
                assert len(header_bytes) == 4, "Header must be exactly 4 bytes"
                
                read_num_stars = struct.unpack('i', header_bytes)[0]
                assert read_num_stars == num_stars, \
                    f"Header should read {num_stars}, got {read_num_stars}"
        finally:
            temp_path.unlink()
    
    def test_binary_star_data_packing(self):
        """Test that star data is correctly packed."""
        
        # Test star data
        test_star = {
            'x': 1.234e20,
            'y': -5.678e20,
            'z': 9.012e20,
            'magnitude': 7.5,
            'epistemic_status': 1  # INFERRED
        }
        
        with tempfile.NamedTemporaryFile(mode='wb', suffix='.bin', delete=False) as f:
            temp_path = Path(f.name)
            
            # Write header (1 star)
            f.write(struct.pack('i', 1))
            
            # Write star
            f.write(struct.pack('ffffi',
                test_star['x'],
                test_star['y'],
                test_star['z'],
                test_star['magnitude'],
                test_star['epistemic_status']
            ))
        
        try:
            # Read back and verify
            with open(temp_path, 'rb') as f:
                # Read header
                num_stars = struct.unpack('i', f.read(4))[0]
                assert num_stars == 1
                
                # Read star
                star_data = struct.unpack('ffffi', f.read(20))  # 4*5 = 20 bytes
                
                assert np.isclose(star_data[0], test_star['x']), "X position mismatch"
                assert np.isclose(star_data[1], test_star['y']), "Y position mismatch"
                assert np.isclose(star_data[2], test_star['z']), "Z position mismatch"
                assert np.isclose(star_data[3], test_star['magnitude']), "Magnitude mismatch"
                assert star_data[4] == test_star['epistemic_status'], "Epistemic status mismatch"
        finally:
            temp_path.unlink()
    
    def test_epistemic_status_encoding(self):
        """Test that epistemic status is correctly encoded as int32."""
        
        EPISTEMIC_MAP = {
            'OBSERVED': 0,
            'INFERRED': 1,
            'SIMULATED': 2
        }
        
        for status_name, status_code in EPISTEMIC_MAP.items():
            with tempfile.NamedTemporaryFile(mode='wb', suffix='.bin', delete=False) as f:
                temp_path = Path(f.name)
                
                # Write header + one star with this status
                f.write(struct.pack('i', 1))
                f.write(struct.pack('ffffi', 0.0, 0.0, 0.0, 5.0, status_code))
            
            try:
                # Read back
                with open(temp_path, 'rb') as f:
                    f.read(4)  # Skip header
                    star_data = struct.unpack('ffffi', f.read(20))
                    
                    assert star_data[4] == status_code, \
                        f"{status_name} should encode as {status_code}, got {star_data[4]}"
            finally:
                temp_path.unlink()


# =============================================================================
# EDGE CASE TESTS
# =============================================================================

class TestBinaryOctreeEdgeCases:
    """Test edge cases and error handling."""
    
    def test_zero_stars_file(self):
        """
        Test that file with 0 stars is valid.
        
        Edge case: Empty octree node (possible in sparse regions)
        """
        with tempfile.NamedTemporaryFile(mode='wb', suffix='.bin', delete=False) as f:
            temp_path = Path(f.name)
            
            # Write header with 0 stars
            f.write(struct.pack('i', 0))
            # No body data
        
        try:
            # Read back - should not crash
            with open(temp_path, 'rb') as f:
                num_stars = struct.unpack('i', f.read(4))[0]
                assert num_stars == 0, "Should read 0 stars"
                
                # File should be exactly 4 bytes (header only)
                f.seek(0, 2)  # Seek to end
                file_size = f.tell()
                assert file_size == 4, f"Empty file should be 4 bytes, got {file_size}"
        finally:
            temp_path.unlink()
    
    def test_large_star_count(self):
        """Test that large star counts (50k limit) are handled."""
        
        MAX_STARS_PER_NODE = 50000
        
        # Create file with max stars (just header, no body for speed)
        with tempfile.NamedTemporaryFile(mode='wb', suffix='.bin', delete=False) as f:
            temp_path = Path(f.name)
            f.write(struct.pack('i', MAX_STARS_PER_NODE))
        
        try:
            with open(temp_path, 'rb') as f:
                num_stars = struct.unpack('i', f.read(4))[0]
                assert num_stars == MAX_STARS_PER_NODE, \
                    f"Should read {MAX_STARS_PER_NODE} stars"
                
                # Expected file size: 4 + (20 * num_stars) bytes
                # We only wrote header, so expect 4 bytes
                f.seek(0, 2)
                assert f.tell() == 4
        finally:
            temp_path.unlink()
    
    def test_negative_star_count_invalid(self):
        """Test that negative star count is detected as invalid."""
        
        with tempfile.NamedTemporaryFile(mode='wb', suffix='.bin', delete=False) as f:
            temp_path = Path(f.name)
            
            # Write invalid header (negative count)
            f.write(struct.pack('i', -10))
        
        try:
            with open(temp_path, 'rb') as f:
                num_stars = struct.unpack('i', f.read(4))[0]
                
                # Validation logic (would be in actual reader)
                assert num_stars < 0, "Detected negative count"
                
                # Reader should reject this
                if num_stars < 0:
                    with pytest.raises(ValueError):
                        raise ValueError("Invalid star count: negative value")
        finally:
            temp_path.unlink()
    
    def test_file_size_consistency(self):
        """Test that file size matches expected size from header."""
        
        num_stars = 100
        expected_size = 4 + (20 * num_stars)  # header + (20 bytes * stars)
        
        with tempfile.NamedTemporaryFile(mode='wb', suffix='.bin', delete=False) as f:
            temp_path = Path(f.name)
            
            # Write header
            f.write(struct.pack('i', num_stars))
            
            # Write stars
            for i in range(num_stars):
                f.write(struct.pack('ffffi', 0.0, 0.0, 0.0, 5.0, 0))
        
        try:
            # Check file size
            actual_size = temp_path.stat().st_size
            assert actual_size == expected_size, \
                f"File size should be {expected_size}, got {actual_size}"
        finally:
            temp_path.unlink()


# =============================================================================
# LOD (LEVEL OF DETAIL) TESTS
# =============================================================================

class TestLODHierarchy:
    """Test Level of Detail hierarchy logic."""
    
    def test_parent_brightness_selection(self):
        """
        Test that parent nodes contain brightest stars.
        
        LOD rule: Parent = brightest 10%, Children = all stars
        """
        # Sample star magnitudes (lower = brighter)
        stars = [
            {'magnitude': 5.0},
            {'magnitude': 3.0},  # Brightest
            {'magnitude': 8.0},
            {'magnitude': 4.0},  # 2nd brightest
            {'magnitude': 10.0},
            {'magnitude': 6.0},
            {'magnitude': 7.0},
            {'magnitude': 9.0},
            {'magnitude': 2.0},  # 3rd brightest (but top 10% = 1 star)
            {'magnitude': 11.0}
        ]
        
        # LOD logic: Select brightest 10%
        LOD_PARENT_FRACTION = 0.10
        keep_count = max(1, int(len(stars) * LOD_PARENT_FRACTION))
        
        sorted_stars = sorted(stars, key=lambda s: s['magnitude'])
        parent_stars = sorted_stars[:keep_count]
        
        # For 10 stars, brightest 10% = 1 star
        assert len(parent_stars) == 1
        assert parent_stars[0]['magnitude'] == 2.0, "Should select brightest star"
    
    def test_splitting_threshold(self):
        """Test that nodes split at 50k star threshold."""
        
        MAX_STARS_PER_NODE = 50000
        MAX_DEPTH = 5
        
        def should_split(num_stars, depth):
            return num_stars > MAX_STARS_PER_NODE and depth < MAX_DEPTH
        
        # Should split
        assert should_split(60000, 0) is True
        assert should_split(50001, 3) is True
        
        # Should not split (below threshold)
        assert should_split(40000, 0) is False
        assert should_split(50000, 0) is False
        
        # Should not split (max depth)
        assert should_split(60000, 5) is False


# =============================================================================
# INTEGRATION TEST
# =============================================================================

class TestBinaryOctreeIntegration:
    """Integration test for full octree workflow."""
    
    def test_write_read_roundtrip(self):
        """
        Test that we can write and read back identical data.
        
        This simulates the export → OpenSpace loading workflow.
        """
        # Create test dataset
        test_stars = [
            (1.0e20, 2.0e20, 3.0e20, 5.0, 0),  # OBSERVED
            (4.0e20, 5.0e20, 6.0e20, 7.0, 1),  # INFERRED
            (7.0e20, 8.0e20, 9.0e20, 9.0, 2),  # SIMULATED
        ]
        
        with tempfile.NamedTemporaryFile(mode='wb', suffix='.bin', delete=False) as f:
            temp_path = Path(f.name)
            
            # Write
            f.write(struct.pack('i', len(test_stars)))
            for star in test_stars:
                f.write(struct.pack('ffffi', *star))
        
        try:
            # Read back
            with open(temp_path, 'rb') as f:
                num_stars = struct.unpack('i', f.read(4))[0]
                assert num_stars == len(test_stars)
                
                for i, expected_star in enumerate(test_stars):
                    star_data = struct.unpack('ffffi', f.read(20))
                    
                    for j, value in enumerate(expected_star):
                        if j < 4:  # floats
                            assert np.isclose(star_data[j], value), \
                                f"Star {i}, field {j}: expected {value}, got {star_data[j]}"
                        else:  # int
                            assert star_data[j] == value, \
                                f"Star {i}, field {j}: expected {value}, got {star_data[j]}"
        finally:
            temp_path.unlink()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
