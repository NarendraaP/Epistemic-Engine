"""
The Epistemic Engine

A visualization framework enforcing epistemological provenance in cosmological data.

This package implements the Three Invariants:
    I.   Labeling (Provenance) - Every data point must have explicit epistemic status
    II.  Reference (Relative Motion) - No absolute coordinates allowed
    III. Access (User Interface) - Truth Slider always shows current epistemic mode
"""

__version__ = "1.0.0"
__author__ = "NarendraaP"
__license__ = "MIT"

# Epistemic status levels
OBSERVED = "L0_OBSERVED"      # White - Direct measurements (Gaia stars)
INFERRED = "L1_INFERRED"      # Gold - Models from observations (Laniakea, Sun orbit)
SIMULATED = "L2_SIMULATED"    # Red - Theoretical/procedural (CMB arrow)

__all__ = ["__version__", "__author__", "__license__", "OBSERVED", "INFERRED", "SIMULATED"]
