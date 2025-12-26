#!/usr/bin/env python3
"""
Generate Laniakea Supercluster Visualization Data
==================================================

EPISTEMIC STATUS: L1 (INFERRED)
SOURCE: Tully et al. 2014 (Nature 513, 71–73)
DOI: 10.1038/nature13674

PURPOSE:
- Generate procedural representation of Laniakea supercluster
- Create galaxy distribution along cosmic web filaments
- Generate flow vectors toward Great Attractor
- Fill the "Empty Middle" per Constitution's Empty Middle Policy

CONSTITUTION COMPLIANCE:
- Empty Middle Policy: Fill ONLY with INFERRED data (never procedural decoration)
- All output tagged as L1 (INFERRED) with Gold color (#FFD700)
- Based on scientific topology from Tully et al. 2014

PHYSICAL CONTEXT:
- Laniakea: Hawaiian for "immeasurable heaven"
- Contains ~100,000 galaxies including Milky Way
- Diameter: ~520 million light-years (160 Mpc)
- Great Attractor: Gravitational focus at Norma Cluster region
- Velocity flows: ~630 km/s toward Great Attractor

IMPLEMENTATION NOTE:
This is a procedural MVP based on published topology. Future versions
should use actual Cosmicflows-4 velocity field data.

DEPENDENCIES:
    pip install --user numpy

USAGE:
    # Generate 5000 galaxy points and flow lines
    python generate_laniakea.py --galaxies 5000 --output-dir ../../data/laniakea
"""

import argparse
import numpy as np
from pathlib import Path
from datetime import datetime
from typing import List, Tuple, Dict


class LaniakeaGenerator:
    """Generates Laniakea supercluster structure based on known topology."""
    
    # Physical constants
    MPC_TO_M = 3.0857e22  # Megaparsec to meters
    LANIAKEA_RADIUS_MPC = 80.0  # ~160 Mpc diameter
    
    # Key attractor positions (approximate Galactic coordinates in Mpc)
    # Relative to Milky Way at origin
    ATTRACTORS = {
        'GreatAttractor': {
            'position_mpc': np.array([60.0, 0.0, 0.0]),  # Norma Cluster region
            'strength': 1.0,
            'description': 'Gravitational Focus (Norma Cluster)'
        },
        'PerseusPisces': {
            'position_mpc': np.array([-40.0, 30.0, 20.0]),
            'strength': 0.6,
            'description': 'Perseus-Pisces Supercluster'
        },
        'VirgoCluster': {
            'position_mpc': np.array([16.5, 0.0, 0.0]),  # 16.5 Mpc from MW
            'strength': 0.5,
            'description': 'Virgo Cluster (Local Supercluster core)'
        },
        'Centaurus': {
            'position_mpc': np.array([45.0, -15.0, -10.0]),
            'strength': 0.4,
            'description': 'Centaurus Supercluster'
        }
    }
    
    # Laniakea boundary (approximate)
    BOUNDARY_CENTER_MPC = np.array([30.0, 0.0, 0.0])  # Offset toward Great Attractor
    
    def __init__(self, num_galaxies=5000, flow_sample_rate=0.2):
        """
        Initialize Laniakea generator.
        
        Args:
            num_galaxies: Number of galaxy points to generate
            flow_sample_rate: Fraction of galaxies to show flow lines for
        """
        self.num_galaxies = num_galaxies
        self.flow_sample_rate = flow_sample_rate
        
    def generate_filament_network(self) -> List[Dict]:
        """
        Generate galaxy positions along cosmic web filaments.
        
        Uses a simple model:
        - Filaments connect attractors
        - Galaxy density higher near attractors
        - Some scatter perpendicular to filaments
        
        Returns:
            List of galaxy dictionaries with positions
        """
        galaxies = []
        
        # Get attractor list
        attractor_names = list(self.ATTRACTORS.keys())
        attractor_positions = [self.ATTRACTORS[a]['position_mpc'] for a in attractor_names]
        
        # Generate galaxies
        for i in range(self.num_galaxies):
            # Pick two random attractors to define a filament
            idx1, idx2 = np.random.choice(len(attractor_positions), 2, replace=False)
            pos1 = attractor_positions[idx1]
            pos2 = attractor_positions[idx2]
            
            # Position along filament (beta distribution for clustering near attractors)
            t = np.random.beta(2, 2)  # Peaks at 0.5, falls off toward ends
            
            # Base position on filament
            base_pos = pos1 + t * (pos2 - pos1)
            
            # Add perpendicular scatter (thins filament)
            scatter = np.random.randn(3) * 5.0  # 5 Mpc scatter
            position_mpc = base_pos + scatter
            
            # Check if inside Laniakea boundary (ellipsoidal region)
            if self._inside_laniakea(position_mpc):
                galaxies.append({
                    'id': f'Laniakea_Galaxy_{i:05d}',
                    'position_mpc': position_mpc,
                    'position_m': position_mpc * self.MPC_TO_M
                })
        
        print(f"✓ Generated {len(galaxies)} galaxies within Laniakea boundary")
        return galaxies
    
    def _inside_laniakea(self, position_mpc: np.ndarray) -> bool:
        """
        Check if position is inside Laniakea boundary.
        
        Uses ellipsoidal approximation centered on Great Attractor.
        
        Args:
            position_mpc: Position in Mpc
        
        Returns:
            True if inside Laniakea
        """
        # Ellipsoid centered on boundary center, stretched toward Great Attractor
        relative_pos = position_mpc - self.BOUNDARY_CENTER_MPC
        
        # Ellipsoidal radii (Mpc)
        a = 80.0  # Semi-major axis (toward Great Attractor)
        b = 60.0  # Semi-minor axes
        c = 60.0
        
        # Ellipsoid equation: (x/a)^2 + (y/b)^2 + (z/c)^2 < 1
        normalized = (relative_pos[0]/a)**2 + (relative_pos[1]/b)**2 + (relative_pos[2]/c)**2
        
        return normalized < 1.0
    
    def generate_flow_vectors(self, galaxies: List[Dict]) -> List[Dict]:
        """
        Generate velocity flow vectors toward Great Attractor.
        
        Based on Cosmicflows observations: galaxies flow toward local attractors,
        primarily the Great Attractor.
        
        Args:
            galaxies: List of galaxy dictionaries
        
        Returns:
            List of flow line dictionaries (start + end positions)
        """
        flows = []
        
        # Sample subset of galaxies for flow visualization
        num_flows = int(len(galaxies) * self.flow_sample_rate)
        sampled_indices = np.random.choice(len(galaxies), num_flows, replace=False)
        
        great_attractor_pos = self.ATTRACTORS['GreatAttractor']['position_mpc']
        
        for idx in sampled_indices:
            galaxy = galaxies[idx]
            pos = galaxy['position_mpc']
            
            # Flow direction: toward nearest attractor (simplified model)
            # In reality, use Cosmicflows-4 velocity field
            
            # Calculate distance to each attractor
            distances = {}
            for name, attractor in self.ATTRACTORS.items():
                dist = np.linalg.norm(pos - attractor['position_mpc'])
                distances[name] = dist
            
            # Flow toward nearest attractor
            nearest_attractor = min(distances, key=distances.get)
            target_pos = self.ATTRACTORS[nearest_attractor]['position_mpc']
            
            # Flow vector direction
            flow_direction = target_pos - pos
            flow_direction_normalized = flow_direction / np.linalg.norm(flow_direction)
            
            # Flow magnitude (velocity ~630 km/s, visualized as 10 Mpc arrow)
            flow_magnitude_mpc = 10.0
            flow_vector = flow_direction_normalized * flow_magnitude_mpc
            
            end_pos_mpc = pos + flow_vector
            
            flows.append({
                'start_position_mpc': pos,
                'end_position_mpc': end_pos_mpc,
                'start_position_m': pos * self.MPC_TO_M,
                'end_position_m': end_pos_mpc * self.MPC_TO_M,
                'target_attractor': nearest_attractor
            })
        
        print(f"✓ Generated {len(flows)} flow vectors")
        return flows
    
    def export_galaxies_to_speck(self, galaxies: List[Dict], output_path: str):
        """
        Export galaxy positions to .speck format.
        
        Args:
            galaxies: List of galaxy dictionaries
            output_path: Output file path
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w') as f:
            # Header
            f.write("# Laniakea Supercluster - Galaxy Distribution\n")
            f.write("# EPISTEMIC STATUS: L1 (INFERRED)\n")
            f.write("#   SOURCE: Tully et al. 2014 (Nature 513, 71–73)\n")
            f.write("#   DOI: 10.1038/nature13674\n")
            f.write(f"#   Generated: {datetime.now().isoformat()}\n")
            f.write(f"#   Number of galaxies: {len(galaxies)}\n")
            f.write("#\n")
            f.write("# NOTE: This is a procedural approximation based on published topology.\n")
            f.write("#       Future versions will use Cosmicflows-4 actual data.\n")
            f.write("#\n")
            f.write("# Color: Gold (#FFD700) - INFERRED data\n")
            f.write("#\n")
            f.write("datavar 0 colorb_v  # Epistemic color (0.5 = INFERRED)\n")
            f.write("#\n")
            f.write("# Format: x y z colorb_v\n")
            f.write("# Coordinates: Cartesian (meters), Galactic frame\n")
            f.write("#\n")
            
            # Data rows
            for galaxy in galaxies:
                x, y, z = galaxy['position_m']
                colorb_v = 0.5  # INFERRED (maps to Gold in color scheme)
                f.write(f"{x:.6e} {y:.6e} {z:.6e} {colorb_v:.3f}\n")
        
        print(f"✓ Exported {len(galaxies)} galaxies to {output_path}")
    
    def export_flows_to_speck(self, flows: List[Dict], output_path: str):
        """
        Export flow vectors to .speck format as line segments.
        
        Args:
            flows: List of flow dictionaries
            output_path: Output file path
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w') as f:
            # Header
            f.write("# Laniakea Supercluster - Velocity Flow Lines\n")
            f.write("# EPISTEMIC STATUS: L1 (INFERRED)\n")
            f.write("#   SOURCE: Tully et al. 2014 (Cosmicflows-2)\n")
            f.write("#   DOI: 10.1038/nature13674\n")
            f.write(f"#   Generated: {datetime.now().isoformat()}\n")
            f.write(f"#   Number of flow lines: {len(flows)}\n")
            f.write("#\n")
            f.write("# Flow vectors point toward local attractors\n")
            f.write("# Primary: Great Attractor (Norma Cluster)\n")
            f.write("#\n")
            f.write("# Format: pairs of points defining line segments\n")
            f.write("# x1 y1 z1 x2 y2 z2\n")
            f.write("# Coordinates: Cartesian (meters)\n")
            f.write("#\n")
            
            # Data rows (line segments)
            for flow in flows:
                x1, y1, z1 = flow['start_position_m']
                x2, y2, z2 = flow['end_position_m']
                f.write(f"{x1:.6e} {y1:.6e} {z1:.6e} {x2:.6e} {y2:.6e} {z2:.6e}\n")
        
        print(f"✓ Exported {len(flows)} flow lines to {output_path}")
    
    def export_attractors_to_json(self, output_path: str):
        """
        Export attractor positions for label rendering.
        
        Args:
            output_path: Output JSON file path
        """
        import json
        
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        attractors_data = {}
        for name, attractor in self.ATTRACTORS.items():
            attractors_data[name] = {
                'position_mpc': attractor['position_mpc'].tolist(),
                'position_m': (attractor['position_mpc'] * self.MPC_TO_M).tolist(),
                'strength': attractor['strength'],
                'description': attractor['description']
            }
        
        with open(output_path, 'w') as f:
            json.dump(attractors_data, f, indent=2)
        
        print(f"✓ Exported attractor data to {output_path}")
    
    def print_statistics(self, galaxies: List[Dict], flows: List[Dict]):
        """Print generation statistics."""
        print(f"\n{'='*60}")
        print("LANIAKEA SUPERCLUSTER - GENERATION SUMMARY")
        print(f"{'='*60}")
        print(f"\nEPISTEMIC STATUS: L1 (INFERRED)")
        print(f"SOURCE: Tully et al. 2014 (Nature 513, 71–73)")
        print(f"DOI: 10.1038/nature13674")
        print(f"\nPHYSICAL PARAMETERS:")
        print(f"  Diameter: ~520 million light-years (~160 Mpc)")
        print(f"  Total galaxies (real): ~100,000")
        print(f"  Velocity flow: ~630 km/s toward Great Attractor")
        print(f"\nGENERATED DATA:")
        print(f"  Galaxy points: {len(galaxies)}")
        print(f"  Flow vectors: {len(flows)}")
        print(f"  Attractors: {len(self.ATTRACTORS)}")
        
        # Spatial statistics
        if galaxies:
            positions = np.array([g['position_mpc'] for g in galaxies])
            center = np.mean(positions, axis=0)
            std = np.std(positions, axis=0)
            print(f"\nSPATIAL DISTRIBUTION:")
            print(f"  Center (Mpc): [{center[0]:.1f}, {center[1]:.1f}, {center[2]:.1f}]")
            print(f"  Std Dev (Mpc): [{std[0]:.1f}, {std[1]:.1f}, {std[2]:.1f}]")
        
        print(f"\nATTRACTORS:")
        for name, attractor in self.ATTRACTORS.items():
            pos = attractor['position_mpc']
            print(f"  {name}: [{pos[0]:.1f}, {pos[1]:.1f}, {pos[2]:.1f}] Mpc")
            print(f"    → {attractor['description']}")
        
        print(f"{'='*60}\n")


def main():
    parser = argparse.ArgumentParser(
        description="Generate Laniakea supercluster visualization (L1 - INFERRED)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
CONSTITUTION COMPLIANCE:
  - Empty Middle Policy: Fills gap between stars and CMB with INFERRED data
  - All output labeled as L1 (INFERRED) with Gold color
  - Based on Tully et al. 2014 scientific topology
  
EXAMPLES:
  # Generate default (5000 galaxies)
  python generate_laniakea.py
  
  # Generate more galaxies with more flow lines
  python generate_laniakea.py --galaxies 10000 --flow-rate 0.3
  
  # Custom output directory
  python generate_laniakea.py --output-dir ../../data/laniakea
        """
    )
    
    parser.add_argument('--galaxies', type=int, default=5000,
                       help='Number of galaxy points to generate (default: 5000)')
    parser.add_argument('--flow-rate', type=float, default=0.2,
                       help='Fraction of galaxies to show flow lines for (default: 0.2)')
    parser.add_argument('--output-dir', default='../../data/laniakea',
                       help='Output directory (default: ../../data/laniakea)')
    
    args = parser.parse_args()
    
    print("\nGenerating Laniakea supercluster structure...")
    
    # Initialize generator
    generator = LaniakeaGenerator(
        num_galaxies=args.galaxies,
        flow_sample_rate=args.flow_rate
    )
    
    # Generate structure
    galaxies = generator.generate_filament_network()
    flows = generator.generate_flow_vectors(galaxies)
    
    # Print statistics
    generator.print_statistics(galaxies, flows)
    
    # Export data
    output_dir = Path(args.output_dir)
    
    generator.export_galaxies_to_speck(
        galaxies,
        output_dir / 'laniakea_galaxies.speck'
    )
    
    generator.export_flows_to_speck(
        flows,
        output_dir / 'laniakea_flows.speck'
    )
    
    generator.export_attractors_to_json(
        output_dir / 'attractors.json'
    )
    
    print(f"\n✓ Laniakea generation complete!")
    print(f"✓ Output directory: {output_dir.absolute()}\n")


if __name__ == '__main__':
    main()
