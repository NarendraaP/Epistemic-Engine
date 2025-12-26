#!/usr/bin/env python3
"""
Epistemic Engine - Build Pipeline Orchestrator
===============================================

PURPOSE: Execute all data generation scripts in the correct order
AUTHOR: Epistemic Engine Project
VERSION: 1.0

WHAT THIS DOES:
1. Validates environment and dependencies
2. Generates kinematic data (Sun's orbit, CMB vector)
3. Ingests Gaia DR3 data (optional - requires database)
4. Generates Laniakea cosmic structure
5. Exports binary octree (optional - requires Gaia data)

USAGE:
    # Run full pipeline (without database steps)
    python run_pipeline.py
    
    # Run full pipeline including database ingestion
    python run_pipeline.py --with-database
    
    # Run specific phases only
    python run_pipeline.py --phases 1,4
    
    # Dry run (show what would be executed)
    python run_pipeline.py --dry-run

REQUIREMENTS:
    - Python 3.7+
    - NumPy installed
    - PostgreSQL + PostGIS (for database steps)
"""

import sys
import subprocess
import time
from pathlib import Path
from typing import List, Tuple, Optional
import argparse


# =============================================================================
# ANSI COLOR CODES FOR TERMINAL OUTPUT
# =============================================================================

class Colors:
    """ANSI color codes for terminal output."""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'


# =============================================================================
# BUILD PIPELINE CONFIGURATION
# =============================================================================

class BuildPhase:
    """Configuration for a build phase."""
    
    def __init__(self, phase_id: int, name: str, script_path: str,
                 args: List[str], success_message: str,
                 requires_database: bool = False):
        self.phase_id = phase_id
        self.name = name
        self.script_path = script_path
        self.args = args
        self.success_message = success_message
        self.requires_database = requires_database


# Define all build phases
BUILD_PHASES = [
    BuildPhase(
        phase_id=1,
        name="Phase 1: Kinematics - Sun's Galactic Orbit",
        script_path="src/ingestion/generate_sun_path.py",
        args=["--samples", "1000", "--output-dir", "data/sun_orbit"],
        success_message="Kinematics Built (Sun's orbit)",
        requires_database=False
    ),
    BuildPhase(
        phase_id=1,
        name="Phase 1: Kinematics - CMB Velocity Vector",
        script_path="src/ingestion/generate_cmb_arrow.py",
        args=["--output-dir", "data/cmb_vector"],
        success_message="Vectors Built (CMB arrow)",
        requires_database=False
    ),
    BuildPhase(
        phase_id=2,
        name="Phase 2: Gaia Ingestion - Database Import",
        script_path="src/ingestion/ingest_gaia.py",
        args=["--limit", "100000", "--magnitude-limit", "12.0"],
        success_message="Gaia Ingested (100k stars)",
        requires_database=True
    ),
    BuildPhase(
        phase_id=2,
        name="Phase 2: Gaia Export - .speck Format",
        script_path="src/ingestion/export_to_speck.py",
        args=["--output", "data/gaia_observed.speck"],
        success_message="Gaia Exported (.speck format)",
        requires_database=True
    ),
    BuildPhase(
        phase_id=4,
        name="Phase 4: Laniakea Structure",
        script_path="src/ingestion/generate_laniakea.py",
        args=["--galaxies", "5000", "--flow-rate", "0.2", "--output-dir", "data/laniakea"],
        success_message="Structure Built (Laniakea)",
        requires_database=False
    ),
    BuildPhase(
        phase_id=5,
        name="Phase 5: Binary Octree Export",
        script_path="src/ingestion/export_binary_octree.py",
        args=["--max-depth", "5", "--output-dir", "data/octree"],
        success_message="Octree Generated (binary format)",
        requires_database=True
    )
]


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def print_header(text: str):
    """Print a formatted header."""
    line = "=" * 70
    print(f"\n{Colors.BOLD}{Colors.CYAN}{line}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{text.center(70)}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{line}{Colors.END}\n")


def print_success(text: str):
    """Print a success message."""
    print(f"{Colors.GREEN}✓ {text}{Colors.END}")


def print_error(text: str):
    """Print an error message."""
    print(f"{Colors.RED}✗ {text}{Colors.END}")


def print_warning(text: str):
    """Print a warning message."""
    print(f"{Colors.YELLOW}⚠ {text}{Colors.END}")


def print_info(text: str):
    """Print an info message."""
    print(f"{Colors.BLUE}ℹ {text}{Colors.END}")


# =============================================================================
# ENVIRONMENT VALIDATION
# =============================================================================

def check_environment() -> bool:
    """
    Validate environment and dependencies.
    
    Returns:
        True if environment is valid, False otherwise
    """
    print_header("ENVIRONMENT CHECK")
    
    all_valid = True
    
    # Check Python version
    python_version = sys.version_info
    if python_version >= (3, 7):
        print_success(f"Python version: {python_version.major}.{python_version.minor}.{python_version.micro}")
    else:
        print_error(f"Python version: {python_version.major}.{python_version.minor}.{python_version.micro} (requires 3.7+)")
        all_valid = False
    
    # Check for required directories
    required_dirs = [
        "src/ingestion",
        "src/db",
        "src/assets",
        "data"
    ]
    
    for dir_path in required_dirs:
        path = Path(dir_path)
        if path.exists():
            print_success(f"Directory exists: {dir_path}")
        else:
            print_error(f"Directory missing: {dir_path}")
            all_valid = False
    
    # Check for required files
    required_files = [
        "src/db/schema.sql",
        "requirements.txt"
    ]
    
    for file_path in required_files:
        path = Path(file_path)
        if path.exists():
            print_success(f"File exists: {file_path}")
        else:
            print_error(f"File missing: {file_path}")
            all_valid = False
    
    # Check for NumPy
    try:
        import numpy
        print_success(f"NumPy installed: {numpy.__version__}")
    except ImportError:
        print_error("NumPy not installed (run: pip install --user numpy)")
        all_valid = False
    
    # Check for all build scripts
    for phase in BUILD_PHASES:
        path = Path(phase.script_path)
        if path.exists():
            print_success(f"Script exists: {phase.script_path}")
        else:
            print_error(f"Script missing: {phase.script_path}")
            all_valid = False
    
    return all_valid


# =============================================================================
# SCRIPT EXECUTION
# =============================================================================

def run_script(script_path: str, args: List[str], dry_run: bool = False) -> Tuple[bool, Optional[str]]:
    """
    Execute a Python script with arguments.
    
    Args:
        script_path: Path to Python script
        args: List of command-line arguments
        dry_run: If True, only show what would be executed
    
    Returns:
        Tuple of (success: bool, error_message: Optional[str])
    """
    cmd = [sys.executable, script_path] + args
    
    if dry_run:
        print_info(f"Would execute: {' '.join(cmd)}")
        return True, None
    
    try:
        # Execute script
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True
        )
        
        # Print output
        if result.stdout:
            print(result.stdout)
        
        return True, None
        
    except subprocess.CalledProcessError as e:
        error_msg = f"Script failed with exit code {e.returncode}"
        if e.stderr:
            error_msg += f"\n{e.stderr}"
        return False, error_msg
    
    except Exception as e:
        return False, str(e)


# =============================================================================
# BUILD PIPELINE ORCHESTRATOR
# =============================================================================

class BuildOrchestrator:
    """Orchestrates the full build pipeline."""
    
    def __init__(self, include_database: bool = False, 
                 selected_phases: Optional[List[int]] = None,
                 dry_run: bool = False):
        """
        Initialize orchestrator.
        
        Args:
            include_database: Whether to include database-dependent steps
            selected_phases: Optional list of phase IDs to run (None = all)
            dry_run: If True, only show what would be executed
        """
        self.include_database = include_database
        self.selected_phases = selected_phases
        self.dry_run = dry_run
        
        self.completed_phases = []
        self.failed_phase = None
        self.start_time = None
    
    def should_run_phase(self, phase: BuildPhase) -> bool:
        """
        Determine if a phase should be executed.
        
        Args:
            phase: BuildPhase to check
        
        Returns:
            True if phase should run
        """
        # Check if phase is in selected phases
        if self.selected_phases is not None:
            if phase.phase_id not in self.selected_phases:
                return False
        
        # Check database requirement
        if phase.requires_database and not self.include_database:
            return False
        
        return True
    
    def run(self) -> bool:
        """
        Execute the full build pipeline.
        
        Returns:
            True if all phases succeeded, False otherwise
        """
        self.start_time = time.time()
        
        print_header("EPISTEMIC ENGINE - BUILD PIPELINE")
        
        print_info(f"Configuration:")
        print(f"  - Include database steps: {self.include_database}")
        print(f"  - Selected phases: {self.selected_phases or 'All'}")
        print(f"  - Dry run: {self.dry_run}")
        print()
        
        # Filter phases to run
        phases_to_run = [p for p in BUILD_PHASES if self.should_run_phase(p)]
        
        if not phases_to_run:
            print_warning("No phases selected to run!")
            return False
        
        print_info(f"Will execute {len(phases_to_run)} build phases\n")
        
        # Execute each phase
        for i, phase in enumerate(phases_to_run, 1):
            print_header(f"STEP {i}/{len(phases_to_run)}: {phase.name}")
            
            if self.dry_run:
                print_info(f"Script: {phase.script_path}")
                print_info(f"Args: {' '.join(phase.args)}")
            
            # Execute phase
            success, error_msg = run_script(phase.script_path, phase.args, self.dry_run)
            
            if success:
                print_success(phase.success_message)
                self.completed_phases.append(phase)
            else:
                print_error(f"FAILED: {phase.name}")
                if error_msg:
                    print_error(f"Error: {error_msg}")
                self.failed_phase = phase
                return False
        
        # All phases completed successfully
        return True
    
    def print_summary(self, success: bool):
        """
        Print build summary.
        
        Args:
            success: Whether build was successful
        """
        elapsed_time = time.time() - self.start_time
        
        print_header("BUILD SUMMARY")
        
        if success:
            print_success(f"BUILD SUCCESSFUL!")
            print_success(f"Completed {len(self.completed_phases)} phases in {elapsed_time:.1f} seconds")
            print()
            print("Generated data files:")
            for phase in self.completed_phases:
                print(f"  ✓ {phase.success_message}")
            print()
            print_info("Next steps:")
            print("  1. Review generated data in data/ directory")
            print("  2. Launch OpenSpace with epistemic_engine_profile.asset")
            print("  3. Use Truth Slider (keys 1/2/3)")
        else:
            print_error(f"BUILD FAILED!")
            print_error(f"Failed at: {self.failed_phase.name if self.failed_phase else 'Unknown'}")
            print()
            print(f"Completed phases: {len(self.completed_phases)}/{len(BUILD_PHASES)}")
            print()
            print_warning("Troubleshooting:")
            print("  1. Check error messages above")
            print("  2. Verify dependencies: pip install -r requirements.txt")
            print("  3. For database steps: Ensure PostgreSQL is running")
            print("  4. Check individual script with: python <script> --help")


# =============================================================================
# MAIN ENTRY POINT
# =============================================================================

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Epistemic Engine Build Pipeline Orchestrator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
EXAMPLES:
  # Run basic pipeline (no database)
  python run_pipeline.py
  
  # Run full pipeline with database steps
  python run_pipeline.py --with-database
  
  # Run only Phase 1 (kinematics)
  python run_pipeline.py --phases 1
  
  # Run Phase 1 and 4 (kinematics + Laniakea)
  python run_pipeline.py --phases 1,4
  
  # Dry run (show what would be executed)
  python run_pipeline.py --dry-run
  
PHASES:
  1 - Kinematics (Sun's orbit, CMB vector)
  2 - Gaia Ingestion (requires database)
  4 - Laniakea Structure
  5 - Binary Octree (requires database)
        """
    )
    
    parser.add_argument('--with-database', action='store_true',
                       help='Include database-dependent steps (Gaia, Octree)')
    parser.add_argument('--phases', type=str,
                       help='Comma-separated list of phase IDs to run (e.g., "1,4")')
    parser.add_argument('--dry-run', action='store_true',
                       help='Show what would be executed without running')
    
    args = parser.parse_args()
    
    # Parse selected phases
    selected_phases = None
    if args.phases:
        try:
            selected_phases = [int(p.strip()) for p in args.phases.split(',')]
        except ValueError:
            print_error("Invalid phase list. Use comma-separated numbers (e.g., '1,4')")
            sys.exit(1)
    
    # Check environment
    if not check_environment():
        print_error("\nEnvironment check failed! Please fix errors above.")
        sys.exit(1)
    
    # Run build pipeline
    orchestrator = BuildOrchestrator(
        include_database=args.with_database,
        selected_phases=selected_phases,
        dry_run=args.dry_run
    )
    
    success = orchestrator.run()
    
    # Print summary
    orchestrator.print_summary(success)
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
