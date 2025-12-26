#!/usr/bin/env python3
"""
Generate Sun's Galactic Orbit Path
===================================

EPISTEMIC STATUS: L1 (INFERRED)
SOURCE: Galactic dynamics models, stellar kinematics observations

This script generates the Sun's inferred orbital path around the Galactic Center,
including vertical oscillation through the galactic plane.

MATHEMATICAL MODEL:
- Orbital Period: ~230 million years (galactic year)
- Vertical Oscillation Period: ~60 million years
- Vertical Amplitude: ~400 parsecs (~1,300 light-years)
- Orbital Radius: ~8.5 kiloparsecs from Galactic Center
- Orbital Velocity: ~220 km/s

CONSTITUTION COMPLIANCE:
- Invariant of Labeling: Output tagged as L1 (INFERRED)
- Invariant of Reference: Motion relative to Galactic Center frame
"""

import numpy as np
import argparse
from pathlib import Path
from datetime import datetime


class SunGalacticOrbitGenerator:
    """Generates the Sun's helical path around the Galactic Center."""
    
    # Physical Constants
    ORBITAL_PERIOD_MYR = 230.0  # Million years
    VERTICAL_PERIOD_MYR = 60.0  # Million years
    VERTICAL_AMPLITUDE_PC = 400.0  # Parsecs
    ORBITAL_RADIUS_KPC = 8.5  # Kiloparsecs
    ORBITAL_VELOCITY_KMS = 220.0  # km/s
    
    # Conversion factors
    PC_TO_M = 3.0857e16  # Parsec to meters
    KPC_TO_M = 3.0857e19  # Kiloparsec to meters
    MYR_TO_S = 3.154e13  # Million years to seconds
    
    def __init__(self, num_samples=10000, time_span_myr=230.0):
        """
        Initialize the orbit generator.
        
        Args:
            num_samples: Number of position samples to generate
            time_span_myr: Time span in million years (default: 1 galactic year)
        """
        self.num_samples = num_samples
        self.time_span_myr = time_span_myr
        
    def generate_orbit(self):
        """
        Generate the helical orbital path.
        
        Returns:
            dict: Contains 'times', 'positions', and 'metadata'
        """
        # Time array (in million years)
        times_myr = np.linspace(0, self.time_span_myr, self.num_samples)
        
        # Angular position (radians)
        # theta = 2π * (t / T_orbital)
        theta = 2 * np.pi * (times_myr / self.ORBITAL_PERIOD_MYR)
        
        # Vertical oscillation
        # z = A * sin(2π * t / T_vertical)
        z_oscillation = self.VERTICAL_AMPLITUDE_PC * np.sin(
            2 * np.pi * times_myr / self.VERTICAL_PERIOD_MYR
        )
        
        # Cartesian coordinates (in parsecs, Galactic frame)
        # X-Y plane: Circular orbit
        # Z axis: Perpendicular to galactic disk
        x_pc = self.ORBITAL_RADIUS_KPC * 1000 * np.cos(theta)
        y_pc = self.ORBITAL_RADIUS_KPC * 1000 * np.sin(theta)
        z_pc = z_oscillation
        
        # Convert to meters for OpenSpace
        positions_m = np.column_stack([
            x_pc * self.PC_TO_M,
            y_pc * self.PC_TO_M,
            z_pc * self.PC_TO_M
        ])
        
        return {
            'times_myr': times_myr,
            'positions_m': positions_m,
            'positions_pc': np.column_stack([x_pc, y_pc, z_pc]),
            'metadata': self._generate_metadata()
        }
    
    def _generate_metadata(self):
        """Generate provenance metadata."""
        return {
            'epistemic_status': 'L1',
            'epistemic_label': 'INFERRED',
            'source': 'Galactic dynamics models',
            'reference_frame': 'Galactic Center',
            'generation_date': datetime.now().isoformat(),
            'parameters': {
                'orbital_period_myr': self.ORBITAL_PERIOD_MYR,
                'vertical_period_myr': self.VERTICAL_PERIOD_MYR,
                'vertical_amplitude_pc': self.VERTICAL_AMPLITUDE_PC,
                'orbital_radius_kpc': self.ORBITAL_RADIUS_KPC,
                'orbital_velocity_kms': self.ORBITAL_VELOCITY_KMS
            },
            'notes': 'Simplified model assuming circular orbit and sinusoidal vertical oscillation'
        }
    
    def export_to_speck(self, output_path, data):
        """
        Export to .speck format for OpenSpace visualization.
        
        Args:
            output_path: Path to output file
            data: Dictionary from generate_orbit()
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w') as f:
            # Header with metadata
            f.write("# Sun's Galactic Orbit\n")
            f.write(f"# EPISTEMIC STATUS: {data['metadata']['epistemic_status']} ({data['metadata']['epistemic_label']})\n")
            f.write(f"# SOURCE: {data['metadata']['source']}\n")
            f.write(f"# REFERENCE FRAME: {data['metadata']['reference_frame']}\n")
            f.write(f"# Generated: {data['metadata']['generation_date']}\n")
            f.write(f"# Orbital Period: {self.ORBITAL_PERIOD_MYR} Myr\n")
            f.write(f"# Vertical Period: {self.VERTICAL_PERIOD_MYR} Myr\n")
            f.write(f"# Vertical Amplitude: {self.VERTICAL_AMPLITUDE_PC} pc\n")
            f.write("#\n")
            f.write("# Format: time_myr x_m y_m z_m\n")
            f.write("#\n")
            
            # Data points
            for i in range(len(data['times_myr'])):
                t = data['times_myr'][i]
                x, y, z = data['positions_m'][i]
                f.write(f"{t:.6f} {x:.6e} {y:.6e} {z:.6e}\n")
        
        print(f"✓ Exported {len(data['times_myr'])} points to {output_path}")
    
    def export_to_csv(self, output_path, data):
        """
        Export to CSV format.
        
        Args:
            output_path: Path to output file
            data: Dictionary from generate_orbit()
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w') as f:
            # CSV header
            f.write("time_myr,x_pc,y_pc,z_pc,x_m,y_m,z_m\n")
            
            # Data rows
            for i in range(len(data['times_myr'])):
                t = data['times_myr'][i]
                x_pc, y_pc, z_pc = data['positions_pc'][i]
                x_m, y_m, z_m = data['positions_m'][i]
                f.write(f"{t:.6f},{x_pc:.6e},{y_pc:.6e},{z_pc:.6e},{x_m:.6e},{y_m:.6e},{z_m:.6e}\n")
        
        print(f"✓ Exported {len(data['times_myr'])} points to {output_path}")
    
    def print_statistics(self, data):
        """Print summary statistics."""
        print("\n" + "="*60)
        print("SUN'S GALACTIC ORBIT - GENERATION SUMMARY")
        print("="*60)
        print(f"\nEPISTEMIC STATUS: {data['metadata']['epistemic_status']} ({data['metadata']['epistemic_label']})")
        print(f"SOURCE: {data['metadata']['source']}")
        print(f"REFERENCE FRAME: {data['metadata']['reference_frame']}")
        print(f"\nPARAMETERS:")
        print(f"  Orbital Period: {self.ORBITAL_PERIOD_MYR} million years")
        print(f"  Vertical Oscillation Period: {self.VERTICAL_PERIOD_MYR} million years")
        print(f"  Vertical Amplitude: {self.VERTICAL_AMPLITUDE_PC} parsecs (~{self.VERTICAL_AMPLITUDE_PC * 3.26:.0f} light-years)")
        print(f"  Orbital Radius: {self.ORBITAL_RADIUS_KPC} kiloparsecs (~{self.ORBITAL_RADIUS_KPC * 3260:.0f} light-years)")
        print(f"  Orbital Velocity: {self.ORBITAL_VELOCITY_KMS} km/s")
        print(f"\nGENERATED DATA:")
        print(f"  Number of samples: {self.num_samples}")
        print(f"  Time span: {self.time_span_myr} million years")
        print(f"  Time resolution: {self.time_span_myr / self.num_samples * 1000:.2f} thousand years/sample")
        
        # Positional statistics
        z_min = np.min(data['positions_pc'][:, 2])
        z_max = np.max(data['positions_pc'][:, 2])
        print(f"\nVERTICAL RANGE:")
        print(f"  Min Z: {z_min:.2f} pc ({z_min * 3.26:.2f} ly)")
        print(f"  Max Z: {z_max:.2f} pc ({z_max * 3.26:.2f} ly)")
        print(f"  Peak-to-peak: {z_max - z_min:.2f} pc ({(z_max - z_min) * 3.26:.2f} ly)")
        print("="*60 + "\n")


def main():
    parser = argparse.ArgumentParser(
        description="Generate Sun's galactic orbit path (L1 - INFERRED)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
EPISTEMIC COMPLIANCE:
  This script enforces the Invariant of Labeling by tagging all
  output as L1 (INFERRED). The model is based on galactic dynamics
  but is a simplified approximation.
  
EXAMPLES:
  # Generate 1 full orbit with default resolution
  python generate_sun_path.py
  
  # Generate 2 full orbits with high resolution
  python generate_sun_path.py --samples 50000 --time-span 460
  
  # Output to custom directory
  python generate_sun_path.py --output-dir ../../data/orbits
        """
    )
    
    parser.add_argument(
        '--samples',
        type=int,
        default=10000,
        help='Number of position samples (default: 10000)'
    )
    
    parser.add_argument(
        '--time-span',
        type=float,
        default=230.0,
        help='Time span in million years (default: 230 = 1 galactic year)'
    )
    
    parser.add_argument(
        '--output-dir',
        type=str,
        default='../../data/sun_orbit',
        help='Output directory (default: ../../data/sun_orbit)'
    )
    
    parser.add_argument(
        '--format',
        choices=['speck', 'csv', 'both'],
        default='both',
        help='Output format (default: both)'
    )
    
    args = parser.parse_args()
    
    # Generate orbit
    print("\nGenerating Sun's galactic orbit...")
    generator = SunGalacticOrbitGenerator(
        num_samples=args.samples,
        time_span_myr=args.time_span
    )
    
    orbit_data = generator.generate_orbit()
    
    # Print statistics
    generator.print_statistics(orbit_data)
    
    # Export data
    output_dir = Path(args.output_dir)
    
    if args.format in ['speck', 'both']:
        generator.export_to_speck(
            output_dir / 'sun_galactic_orbit.speck',
            orbit_data
        )
    
    if args.format in ['csv', 'both']:
        generator.export_to_csv(
            output_dir / 'sun_galactic_orbit.csv',
            orbit_data
        )
    
    print(f"\n✓ Sun's galactic orbit generation complete!")
    print(f"✓ Output directory: {output_dir.absolute()}\n")


if __name__ == '__main__':
    main()
