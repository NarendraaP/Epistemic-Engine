#!/usr/bin/env python3
"""
Export Gaia Data to OpenSpace .speck Format
============================================

EPISTEMIC STATUS: Exports L0 (OBSERVED) data from database to visualization format.

PURPOSE:
- Read cosmic_objects from PostGIS database
- Convert to OpenSpace .speck format (text-based, chunked)
- Apply epistemic color coding (White/Blue for OBSERVED)
- Include magnitude-based sizing

OUTPUT FORMAT (.speck):
    # Header with metadata
    datavar 0 colorb_v  # Color (based on epistemic status)
    datavar 1 lum       # Luminosity (for sizing)
    <x> <y> <z> <colorb_v> <lum> # One star per line

DEPENDENCIES:
    pip install --user psycopg2-binary numpy

USAGE:
    # Export all OBSERVED stars
    python export_to_speck.py --output ../../data/gaia_observed.speck
    
    # Export only bright stars
    python export_to_speck.py --magnitude-limit 10.0 --output ../../data/gaia_bright.speck
"""

import argparse
import sys
from datetime import datetime
from typing import Dict, List

try:
    import numpy as np
    import psycopg2
except ImportError as e:
    print(f"ERROR: Missing dependency: {e}")
    print("Install with: pip install --user psycopg2-binary numpy")
    sys.exit(1)


class SpeckExporter:
    """Exports cosmic_objects to .speck format for OpenSpace."""
    
    # Epistemic color mapping (Constitution Layer 3)
    EPISTEMIC_COLORS = {
        'OBSERVED': 1.0,    # White/Blue (full brightness)
        'INFERRED': 0.5,    # Gold (medium brightness for datavar)
        'SIMULATED': 0.2    # Red (low brightness for datavar)
    }
    
    def __init__(self, db_config: Dict[str, str]):
        """
        Initialize exporter.
        
        Args:
            db_config: Database connection parameters
        """
        self.db_config = db_config
        self.conn = None
        self.cursor = None
    
    def connect_db(self):
        """Establish database connection."""
        try:
            self.conn = psycopg2.connect(**self.db_config)
            self.cursor = self.conn.cursor()
            print(f"✓ Connected to database: {self.db_config['database']}")
        except Exception as e:
            print(f"✗ Database connection failed: {e}")
            sys.exit(1)
    
    def query_stars(self, epistemic_filter: str = 'OBSERVED', magnitude_limit: float = None) -> List[Dict]:
        """
        Query stars from database.
        
        Args:
            epistemic_filter: Filter by truth_label (default: OBSERVED)
            magnitude_limit: Optional magnitude cutoff
        
        Returns:
            List of star dictionaries with Cartesian coordinates
        """
        print(f"\n{'='*60}")
        print("QUERYING DATABASE")
        print(f"{'='*60}")
        print(f"Epistemic filter: {epistemic_filter}")
        if magnitude_limit:
            print(f"Magnitude limit: G < {magnitude_limit}")
        
        # Build query
        query = """
            SELECT 
                id,
                truth_label,
                ST_X(location::geometry) AS ra,
                ST_Y(location::geometry) AS dec,
                ST_Z(location::geometry) AS distance_pc,
                magnitude_g,
                color_index_bp_rp,
                provenance
            FROM cosmic_objects
            WHERE truth_label = %s
        """
        
        params = [epistemic_filter]
        
        if magnitude_limit:
            query += " AND magnitude_g < %s"
            params.append(magnitude_limit)
        
        query += " ORDER BY magnitude_g ASC"
        
        try:
            self.cursor.execute(query, params)
            rows = self.cursor.fetchall()
            
            stars = []
            for row in rows:
                stars.append({
                    'id': row[0],
                    'truth_label': row[1],
                    'ra': row[2],
                    'dec': row[3],
                    'distance_pc': row[4],
                    'magnitude_g': row[5],
                    'color_bp_rp': row[6],
                    'provenance': row[7]
                })
            
            print(f"✓ Retrieved {len(stars)} stars")
            return stars
            
        except Exception as e:
            print(f"✗ Query failed: {e}")
            sys.exit(1)
    
    def spherical_to_cartesian(self, ra_deg: float, dec_deg: float, distance_pc: float) -> tuple:
        """
        Convert spherical (RA, Dec, Distance) to Cartesian (X, Y, Z).
        
        Args:
            ra_deg: Right Ascension in degrees
            dec_deg: Declination in degrees
            distance_pc: Distance in parsecs
        
        Returns:
            (x, y, z) in parsecs
        """
        # Convert to radians
        ra = np.radians(ra_deg)
        dec = np.radians(dec_deg)
        
        # Spherical to Cartesian
        x = distance_pc * np.cos(dec) * np.cos(ra)
        y = distance_pc * np.cos(dec) * np.sin(ra)
        z = distance_pc * np.sin(dec)
        
        return (x, y, z)
    
    def magnitude_to_luminosity(self, magnitude: float) -> float:
        """
        Convert apparent magnitude to relative luminosity for sizing.
        
        Brighter stars (lower magnitude) get larger size.
        
        Args:
            magnitude: Apparent magnitude
        
        Returns:
            Relative luminosity (0.0 to 1.0)
        """
        # Normalize magnitude to 0-1 range
        # Bright stars: mag ~ 0, Faint stars: mag ~ 15
        # Invert so bright = 1.0, faint = 0.0
        normalized = 1.0 - (magnitude / 15.0)
        return max(0.0, min(1.0, normalized))  # Clamp to [0, 1]
    
    def export_to_speck(self, stars: List[Dict], output_path: str):
        """
        Export stars to .speck format.
        
        Args:
            stars: List of star dictionaries
            output_path: Output file path
        """
        print(f"\n{'='*60}")
        print("EXPORTING TO .SPECK FORMAT")
        print(f"{'='*60}")
        print(f"Output file: {output_path}")
        
        with open(output_path, 'w') as f:
            # Header
            f.write("# OpenSpace .speck format\n")
            f.write("# Epistemic Engine - Gaia DR3 OBSERVED Data\n")
            f.write(f"# Generated: {datetime.now().isoformat()}\n")
            f.write(f"# Number of stars: {len(stars)}\n")
            f.write("#\n")
            f.write("# EPISTEMIC STATUS: OBSERVED (L0)\n")
            f.write("#  SOURCE: Gaia DR3\n")
            f.write("#  COLOR: White/Blue (Constitution Layer 3)\n")
            f.write("#\n")
            f.write("# Data variables:\n")
            f.write("datavar 0 colorb_v  # Epistemic color (1.0 = OBSERVED)\n")
            f.write("datavar 1 lum       # Luminosity (magnitude-based sizing)\n")
            f.write("#\n")
            f.write("# Format: x y z colorb_v lum\n")
            f.write("# Coordinates: Cartesian (parsecs), ICRS frame\n")
            f.write("#\n")
            
            # Data rows
            count = 0
            for star in stars:
                # Convert to Cartesian
                x, y, z = self.spherical_to_cartesian(
                    star['ra'],
                    star['dec'],
                    star['distance_pc']
                )
                
                # Epistemic color
                colorb_v = self.EPISTEMIC_COLORS[star['truth_label']]
                
                # Luminosity (for sizing)
                lum = self.magnitude_to_luminosity(star['magnitude_g'])
                
                # Write row
                f.write(f"{x:.6e} {y:.6e} {z:.6e} {colorb_v:.3f} {lum:.6f}\n")
                count += 1
            
        print(f"✓ Exported {count} stars to {output_path}")
        
        # File statistics
        import os
        file_size = os.path.getsize(output_path)
        print(f"  File size: {file_size / 1024 / 1024:.2f} MB")
    
    def close(self):
        """Close database connection."""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()


def main():
    parser = argparse.ArgumentParser(
        description="Export cosmic_objects to OpenSpace .speck format",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
CONSTITUTION COMPLIANCE:
  - Only exports OBSERVED data by default (Invariant III: Access)
  - Color-coded by epistemic status
  - Magnitude-based sizing
  
EXAMPLES:
  # Export all OBSERVED stars
  python export_to_speck.py --output gaia_observed.speck
  
  # Export only bright stars
  python export_to_speck.py --magnitude-limit 10.0
  
  # Custom database
  python export_to_speck.py --db-name epistemic_engine --output gaia.speck
        """
    )
    
    parser.add_argument('--output', default='../../data/gaia_observed.speck',
                       help='Output .speck file path')
    parser.add_argument('--epistemic-filter', default='OBSERVED',
                       choices=['OBSERVED', 'INFERRED', 'SIMULATED'],
                       help='Filter by epistemic status (default: OBSERVED)')
    parser.add_argument('--magnitude-limit', type=float,
                       help='Optional magnitude cutoff')
    parser.add_argument('--db-host', default='localhost',
                       help='Database host (default: localhost)')
    parser.add_argument('--db-port', default='5432',
                       help='Database port (default: 5432)')
    parser.add_argument('--db-name', default='epistemic_engine',
                       help='Database name (default: epistemic_engine)')
    parser.add_argument('--db-user', default='postgres',
                       help='Database user (default: postgres)')
    parser.add_argument('--db-password', default='',
                       help='Database password')
    
    args = parser.parse_args()
    
    # Database configuration
    db_config = {
        'host': args.db_host,
        'port': args.db_port,
        'database': args.db_name,
        'user': args.db_user,
        'password': args.db_password
    }
    
    # Execute export
    exporter = SpeckExporter(db_config)
    
    try:
        # 1. Connect to database
        exporter.connect_db()
        
        # 2. Query stars
        stars = exporter.query_stars(
            epistemic_filter=args.epistemic_filter,
            magnitude_limit=args.magnitude_limit
        )
        
        if not stars:
            print("⚠️  No stars found matching criteria")
            sys.exit(0)
        
        # 3. Export to .speck
        exporter.export_to_speck(stars, args.output)
        
        print(f"\n✓ Export complete!")
        print(f"  Load in OpenSpace with: asset.require('{args.output}')")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Export interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Fatal error: {e}")
        sys.exit(1)
    finally:
        exporter.close()


if __name__ == '__main__':
    main()
