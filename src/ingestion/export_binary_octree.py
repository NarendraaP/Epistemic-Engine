#!/usr/bin/env python3
"""
Binary Octree Exporter for Large-Scale Star Catalogs
=====================================================

PURPOSE: Export millions of stars from PostGIS to binary octree format for
         efficient LOD (Level of Detail) rendering in OpenSpace.

PERFORMANCE TARGET: Handle 1+ million stars (full Gaia subset)

OCTREE STRUCTURE:
- Recursive spatial subdivision into 8 octants
- LOD hierarchy: Parent nodes store brightest 10% of stars
- Splitting rule: If stars > 50,000 AND depth < MAX_DEPTH → split
- Binary format for fast I/O

BINARY FILE FORMAT (.bin):
    Header:
        - num_stars (int32): Number of stars in this node
    Body (per star):
        - position_x (float32): X coordinate in meters
        - position_y (float32): Y coordinate in meters
        - position_z (float32): Z coordinate in meters
        - magnitude (float32): Apparent magnitude
        - epistemic_status (int32): 0=OBSERVED, 1=INFERRED, 2=SIMULATED

FILE NAMING: {depth}-{x}-{y}-{z}.bin
    Example: 0-0-0-0.bin (root), 1-0-0-0.bin (first child), etc.

DEPENDENCIES:
    pip install --user psycopg2-binary numpy

USAGE:
    # Export octree from database
    python export_binary_octree.py --max-depth 5 --output-dir ../../data/octree
    
    # Export specific epistemic level
    python export_binary_octree.py --epistemic-filter OBSERVED --max-depth 4
"""

import argparse
import struct
import sys
from pathlib import Path
from typing import List, Tuple, Dict, Optional
from dataclasses import dataclass

try:
    import numpy as np
    import psycopg2
except ImportError as e:
    print(f"ERROR: Missing dependency: {e}")
    print("Install with: pip install --user psycopg2-binary numpy")
    sys.exit(1)


@dataclass
class BoundingBox:
    """3D bounding box for octree nodes."""
    min_x: float
    max_x: float
    min_y: float
    max_y: float
    min_z: float
    max_z: float
    
    def get_center(self) -> Tuple[float, float, float]:
        """Get center point of bounding box."""
        return (
            (self.min_x + self.max_x) / 2,
            (self.min_y + self.max_y) / 2,
            (self.min_z + self.max_z) / 2
        )
    
    def get_octant(self, octant_index: int) -> 'BoundingBox':
        """
        Get bounding box for one of 8 octants.
        
        Octant indexing (binary):
            000 (0): -x, -y, -z
            001 (1): -x, -y, +z
            010 (2): -x, +y, -z
            011 (3): -x, +y, +z
            100 (4): +x, -y, -z
            101 (5): +x, -y, +z
            110 (6): +x, +y, -z
            111 (7): +x, +y, +z
        """
        cx, cy, cz = self.get_center()
        
        # Decode octant bits
        x_half = 1 if (octant_index & 0b100) else 0
        y_half = 1 if (octant_index & 0b010) else 0
        z_half = 1 if (octant_index & 0b001) else 0
        
        # Calculate octant bounds
        if x_half == 0:
            new_min_x, new_max_x = self.min_x, cx
        else:
            new_min_x, new_max_x = cx, self.max_x
        
        if y_half == 0:
            new_min_y, new_max_y = self.min_y, cy
        else:
            new_min_y, new_max_y = cy, self.max_y
        
        if z_half == 0:
            new_min_z, new_max_z = self.min_z, cz
        else:
            new_min_z, new_max_z = cz, self.max_z
        
        return BoundingBox(
            new_min_x, new_max_x,
            new_min_y, new_max_y,
            new_min_z, new_max_z
        )


@dataclass
class Star:
    """Star data for binary export."""
    position_x: float
    position_y: float
    position_z: float
    magnitude: float
    epistemic_status: int  # 0=OBSERVED, 1=INFERRED, 2=SIMULATED


class BinaryOctreeBuilder:
    """Builds binary octree structure from PostGIS database."""
    
    # Epistemic status mapping
    EPISTEMIC_MAP = {
        'OBSERVED': 0,
        'INFERRED': 1,
        'SIMULATED': 2
    }
    
    # Octree parameters
    MAX_STARS_PER_NODE = 50000  # Split if more than this
    LOD_PARENT_FRACTION = 0.10  # Keep brightest 10% in parent
    
    def __init__(self, db_config: Dict[str, str], max_depth: int = 5,
                 epistemic_filter: Optional[str] = None):
        """
        Initialize octree builder.
        
        Args:
            db_config: Database connection parameters
            max_depth: Maximum octree depth (default: 5)
            epistemic_filter: Optional filter for epistemic status
        """
        self.db_config = db_config
        self.max_depth = max_depth
        self.epistemic_filter = epistemic_filter
        self.conn = None
        self.cursor = None
        
        # Statistics
        self.total_nodes = 0
        self.total_stars_exported = 0
        
    def connect_db(self):
        """Establish database connection."""
        try:
            self.conn = psycopg2.connect(**self.db_config)
            self.cursor = self.conn.cursor()
            print(f"✓ Connected to database: {self.db_config['database']}")
        except Exception as e:
            print(f"✗ Database connection failed: {e}")
            sys.exit(1)
    
    def get_global_bounds(self) -> BoundingBox:
        """
        Calculate global bounding box from all stars in database.
        
        Returns:
            BoundingBox encompassing all stars
        """
        query = """
            SELECT 
                MIN(ST_X(location::geometry)) AS min_x,
                MAX(ST_X(location::geometry)) AS max_x,
                MIN(ST_Y(location::geometry)) AS min_y,
                MAX(ST_Y(location::geometry)) AS max_y,
                MIN(ST_Z(location::geometry)) AS min_z,
                MAX(ST_Z(location::geometry)) AS max_z
            FROM cosmic_objects
        """
        
        if self.epistemic_filter:
            query += f" WHERE truth_label = '{self.epistemic_filter}'"
        
        self.cursor.execute(query)
        row = self.cursor.fetchone()
        
        # Convert RA/Dec/Distance to Cartesian bounds (already in DB as POINTZ)
        # Add 10% padding
        padding = 0.1
        min_x, max_x = row[0] * (1 - padding), row[1] * (1 + padding)
        min_y, max_y = row[2] * (1 - padding), row[3] * (1 + padding)
        min_z, max_z = row[4] * (1 - padding), row[5] * (1 + padding)
        
        bounds = BoundingBox(min_x, max_x, min_y, max_y, min_z, max_z)
        print(f"✓ Global bounds calculated:")
        print(f"  X: [{min_x:.2e}, {max_x:.2e}]")
        print(f"  Y: [{min_y:.2e}, {max_y:.2e}]")
        print(f"  Z: [{min_z:.2e}, {max_z:.2e}]")
        
        return bounds
    
    def query_stars_in_bounds(self, bounds: BoundingBox) -> List[Star]:
        """
        Query stars within bounding box.
        
        Args:
            bounds: Bounding box to query
        
        Returns:
            List of Star objects
        """
        query = """
            SELECT 
                ST_X(location::geometry) AS x,
                ST_Y(location::geometry) AS y,
                ST_Z(location::geometry) AS z,
                magnitude_g,
                truth_label
            FROM cosmic_objects
            WHERE 
                ST_X(location::geometry) BETWEEN %s AND %s
                AND ST_Y(location::geometry) BETWEEN %s AND %s
                AND ST_Z(location::geometry) BETWEEN %s AND %s
        """
        
        params = [
            bounds.min_x, bounds.max_x,
            bounds.min_y, bounds.max_y,
            bounds.min_z, bounds.max_z
        ]
        
        if self.epistemic_filter:
            query += " AND truth_label = %s"
            params.append(self.epistemic_filter)
        
        self.cursor.execute(query, params)
        rows = self.cursor.fetchall()
        
        stars = []
        for row in rows:
            x, y, z, mag, truth_label = row
            stars.append(Star(
                position_x=float(x),
                position_y=float(y),
                position_z=float(z),
                magnitude=float(mag) if mag is not None else 15.0,
                epistemic_status=self.EPISTEMIC_MAP.get(truth_label, 0)
            ))
        
        return stars
    
    def select_lod_subset(self, stars: List[Star], fraction: float) -> List[Star]:
        """
        Select brightest fraction of stars for LOD parent node.
        
        Args:
            stars: Full star list
            fraction: Fraction to keep (e.g., 0.10 for 10%)
        
        Returns:
            Subset of brightest stars
        """
        if not stars:
            return []
        
        # Sort by magnitude (lower = brighter)
        sorted_stars = sorted(stars, key=lambda s: s.magnitude)
        
        # Take brightest fraction
        keep_count = max(1, int(len(sorted_stars) * fraction))
        return sorted_stars[:keep_count]
    
    def export_node_binary(self, stars: List[Star], output_path: Path):
        """
        Export stars to binary file.
        
        Binary format:
            Header: int32 num_stars
            Body: For each star:
                - float32 x, y, z (position)
                - float32 magnitude
                - int32 epistemic_status
        
        Args:
            stars: List of stars to export
            output_path: Output .bin file path
        """
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'wb') as f:
            # Header: number of stars
            f.write(struct.pack('i', len(stars)))
            
            # Body: star data
            for star in stars:
                # Pack: 3 floats (position) + 1 float (magnitude) + 1 int (status)
                # Format: 'ffffi' = 3 * float32 + 1 * float32 + 1 * int32
                packed = struct.pack(
                    'ffffi',
                    star.position_x,
                    star.position_y,
                    star.position_z,
                    star.magnitude,
                    star.epistemic_status
                )
                f.write(packed)
        
        self.total_stars_exported += len(stars)
    
    def build_octree(self, bounds: BoundingBox, depth: int, 
                    octant_path: Tuple[int, ...], output_dir: Path):
        """
        Recursively build octree structure.
        
        Args:
            bounds: Bounding box for current node
            depth: Current depth in octree
            octant_path: Path tuple (e.g., (0,), (0, 3), (0, 3, 7))
            output_dir: Base output directory
        """
        # Query stars in this node
        stars = self.query_stars_in_bounds(bounds)
        num_stars = len(stars)
        
        # Generate node filename
        if depth == 0:
            node_file = output_dir / "0-0-0-0.bin"  # Root
        else:
            # Format: depth-x-y-z.bin (octant path encoded)
            path_str = '-'.join(map(str, octant_path))
            node_file = output_dir / f"{depth}-{path_str}.bin"
        
        print(f"  Depth {depth}, Octant {octant_path}: {num_stars} stars")
        
        # Check if we should split
        should_split = (
            num_stars > self.MAX_STARS_PER_NODE and
            depth < self.max_depth
        )
        
        if should_split:
            # LOD: Save brightest 10% in parent node for distant viewing
            lod_stars = self.select_lod_subset(stars, self.LOD_PARENT_FRACTION)
            self.export_node_binary(lod_stars, node_file)
            self.total_nodes += 1
            
            # Recursively build children
            for octant_idx in range(8):
                child_bounds = bounds.get_octant(octant_idx)
                child_path = octant_path + (octant_idx,)
                self.build_octree(child_bounds, depth + 1, child_path, output_dir)
        
        else:
            # Leaf node: export all stars
            self.export_node_binary(stars, node_file)
            self.total_nodes += 1
    
    def build(self, output_dir: Path):
        """
        Build complete octree structure.
        
        Args:
            output_dir: Output directory for .bin files
        """
        print(f"\n{'='*60}")
        print("BINARY OCTREE EXPORT")
        print(f"{'='*60}")
        print(f"Max depth: {self.max_depth}")
        print(f"Max stars per node: {self.MAX_STARS_PER_NODE}")
        print(f"LOD parent fraction: {self.LOD_PARENT_FRACTION * 100}%")
        if self.epistemic_filter:
            print(f"Epistemic filter: {self.epistemic_filter}")
        print()
        
        # Get global bounds
        global_bounds = self.get_global_bounds()
        
        # Build octree
        print("\nBuilding octree...")
        self.build_octree(global_bounds, depth=0, octant_path=(), output_dir=output_dir)
        
        # Statistics
        print(f"\n{'='*60}")
        print("EXPORT COMPLETE")
        print(f"{'='*60}")
        print(f"Total nodes: {self.total_nodes}")
        print(f"Total stars exported: {self.total_stars_exported}")
        print(f"Output directory: {output_dir.absolute()}")
        print(f"{'='*60}\n")
    
    def close(self):
        """Close database connection."""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()


def main():
    parser = argparse.ArgumentParser(
        description="Export star catalog to binary octree format",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
PERFORMANCE:
  Binary format enables handling 1+ million stars with LOD rendering.
  
OCTREE STRUCTURE:
  - Parent nodes store brightest 10% for distant viewing
  - Child nodes store full detail for close-up
  - Recursive splitting at 50k stars per node
  
EXAMPLES:
  # Export octree from database
  python export_binary_octree.py --max-depth 5
  
  # Export only OBSERVED stars
  python export_binary_octree.py --epistemic-filter OBSERVED
        """
    )
    
    parser.add_argument('--max-depth', type=int, default=5,
                       help='Maximum octree depth (default: 5)')
    parser.add_argument('--epistemic-filter', 
                       choices=['OBSERVED', 'INFERRED', 'SIMULATED'],
                       help='Filter by epistemic status')
    parser.add_argument('--output-dir', default='../../data/octree',
                       help='Output directory (default: ../../data/octree)')
    parser.add_argument('--db-host', default='localhost',
                       help='Database host')
    parser.add_argument('--db-port', default='5432',
                       help='Database port')
    parser.add_argument('--db-name', default='epistemic_engine',
                       help='Database name')
    parser.add_argument('--db-user', default='postgres',
                       help='Database user')
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
    
    # Build octree
    builder = BinaryOctreeBuilder(
        db_config=db_config,
        max_depth=args.max_depth,
        epistemic_filter=args.epistemic_filter
    )
    
    try:
        builder.connect_db()
        builder.build(Path(args.output_dir))
    except KeyboardInterrupt:
        print("\n\n⚠️  Export interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        builder.close()


if __name__ == '__main__':
    main()
