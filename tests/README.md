# Epistemic Engine - Test Suite

## Overview

The test suite enforces the **Epistemic Constitution** by validating that all code complies with the Three Invariants.

## Test Files

### 1. `test_invariants.py` - Constitutional Compliance
Tests enforcement of all three invariants:

**Invariant I (Labeling):**
- Null `truth_label` is rejected
- Invalid epistemic statuses are rejected
- Null `provenance` is rejected
- Valid labels (OBSERVED/INFERRED/SIMULATED) are accepted

**Invariant II (Reference):**
- Parallax to distance conversion works correctly
- Negative/zero parallax is rejected (unphysical)
- Spherical to Cartesian conversion is accurate
- No absolute coordinates allowed

**Invariant III (Access):**
- Truth Slider has exactly 3 levels
- Invalid truth levels are rejected
- All epistemic statuses have color mappings

### 2. `test_octree.py` - Binary Format Validation
Tests binary octree structure:

**Binary Format:**
- Header contains correct int32 star count
- Star data is correctly packed (position + magnitude + epistemic status)
- Epistemic status encoding (0=OBSERVED, 1=INFERRED, 2=SIMULATED)

**Edge Cases:**
- Files with 0 stars are valid
- Large star counts (50k limit) are handled
- Negative star counts are detected as invalid
- File size matches expected size from header

**LOD (Level of Detail):**
- Parent nodes select brightest 10%
- Splitting threshold (50k stars) works correctly

### 3. `test_schema.py` - Database Schema Validation
Tests PostgreSQL schema compliance:

**Schema Structure:**
- `epistemic_status_type` enum exists
- Enum contains OBSERVED, INFERRED, SIMULATED
- `cosmic_objects` table exists
- `truth_label` has NOT NULL constraint
- `provenance` is JSONB NOT NULL

**Spatial Features:**
- `location` uses GEOGRAPHY(POINTZ) (not GEOMETRY)
- GIST index exists on location
- Index exists on truth_label (for Truth Slider)

**Constitutional Compliance:**
- No absolute coordinate columns
- PostGIS extension enabled
- All three invariants enforced at schema level

## Running Tests

### Run All Tests
```bash
pytest tests/
```

### Run Specific Test File
```bash
pytest tests/test_invariants.py
pytest tests/test_octree.py
pytest tests/test_schema.py
```

### Run with Verbose Output
```bash
pytest tests/ -v
```

### Run Specific Test Class
```bash
pytest tests/test_invariants.py::TestInvariantI_Labeling
```

### Run Specific Test Function
```bash
pytest tests/test_invariants.py::TestInvariantI_Labeling::test_null_truth_label_rejected
```

### Run Tests by Marker
```bash
# Run only Invariant I tests
pytest tests/ -m invariant_i

# Run only schema tests
pytest tests/ -m schema

# Run only binary format tests
pytest tests/ -m binary
```

### Run with Coverage (requires pytest-cov)
```bash
pip install pytest-cov
pytest tests/ --cov=src --cov-report=html
```

## Test Statistics

**Total Tests:** ~30+

**Coverage:**
- Invariant I (Labeling): 5 tests
- Invariant II (Reference): 4 tests
- Invariant III (Access): 3 tests
- Binary Octree Format: 8 tests
- Database Schema: 12+ tests
- Integration: 2 tests

## Expected Output

```
==================== test session starts ====================
tests/test_invariants.py::TestInvariantI_Labeling::test_null_truth_label_rejected PASSED
tests/test_invariants.py::TestInvariantI_Labeling::test_invalid_truth_label_rejected PASSED
tests/test_invariants.py::TestInvariantI_Labeling::test_valid_truth_labels_accepted PASSED
...
tests/test_schema.py::TestDatabaseSchema::test_epistemic_status_enum_exists PASSED
tests/test_schema.py::TestDatabaseSchema::test_truth_label_not_null PASSED

==================== 30 passed in 0.5s ====================
```

## CI/CD Integration

Add to your CI pipeline:

```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.7'
      - name: Install dependencies
        run: |
          pip install pytest numpy
      - name: Run tests
        run: pytest tests/ -v
```

## Continuous Compliance

These tests act as "The Epistemic Guard" - ensuring that:

1. **No unlabeled data** enters the system (Invariant I)
2. **No absolute coordinates** are used (Invariant II)
3. **Truth Slider** maintains correct structure (Invariant III)
4. **Binary format** remains consistent
5. **Database schema** enforces Constitutional rules

**Before every commit, run:**
```bash
pytest tests/
```

If all tests pass ✅, the Constitution is upheld!

## Adding New Tests

When adding features, ensure tests verify:

1. **Labeling:** New data has `truth_label` and `provenance`
2. **Reference:** Coordinates are relative, not absolute
3. **Access:** UI changes maintain epistemic clarity

Follow existing test structure:
```python
class TestNewFeature:
    def test_feature_enforces_constitution(self):
        # Setup
        data = {...}
        
        # Execute
        result = process(data)
        
        # Assert Constitutional compliance
        assert result['truth_label'] in ['OBSERVED', 'INFERRED', 'SIMULATED']
```

---

**"The Constitution is code, and code is the Constitution."**
