#!/usr/bin/env python3
"""
Gaia DR3 Data Ingestion Script
===============================

EPISTEMIC STATUS: This script ingests L0 (OBSERVED) data from Gaia DR3.

PURPOSE:
- Query Gaia DR3 via ESA TAP service
- Adjudicate epistemic status (OBSERVED for all Gaia data)
- Validate provenance and error margins
- Insert into PostGIS database

CONSTITUTION COMPLIANCE:
- Invariant I (Labeling): All rows get truth_label='OBSERVED' + provenance
- Invariant II (Reference): Spherical coords (RA, Dec, Distance from parallax)
- Rejects any star without parallax error (no error margin = no ingestion)

DEPENDENCIES:
    pip install --user astroquery psycopg2-binary numpy

USAGE:
    # Ingest 100k brightest stars
    python ingest_gaia.py --limit 100000 --magnitude-limit 12.0
    
    # Test with small sample
    python ingest_gaia.py --limit 100 --test
"""

import argparse
import json
import sys
from datetime import datetime
from typing import Dict, List, Optional

try:
    import numpy as np
    from astroquery.gaia import Gaia
    import psycopg2
    from psycopg2.extras import execute_values
except ImportError as e:
    print(f"ERROR: Missing dependency: {e}")
    print("Install with: pip install --user astroquery psycopg2-binary numpy")
    sys.exit(1)


class GaiaIngestionPipeline:
    """Ingests Gaia DR3 data enforcing Constitutional invariants."""
    
    # Provenance metadata
    GAIA_DR3_DOI = "10.1051/0004-6361/202243940"
    GAIA_DR3_SOURCE = "Gaia DR3"
    GAIA_DR3_RELEASE_DATE = "2022-06-13"
    
    def __init__(self, db_config: Dict[str, str]):
        """
        Initialize ingestion pipeline.
        
        Args:
            db_config: Database connection parameters
                {host, port, database, user, password}
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
    
    def query_gaia(self, limit: int = 100000, magnitude_limit: float = 12.0) -> List[Dict]:
        """
        Query Gaia DR3 for bright stars.
        
        Args:
            limit: Maximum number of stars to fetch
            magnitude_limit: Magnitude cutoff (brighter = smaller number)
        
        Returns:
            List of star dictionaries with Gaia data
        """
        print(f"\n{'='*60}")
        print("QUERYING GAIA DR3")
        print(f"{'='*60}")
        print(f"Magnitude limit: G < {magnitude_limit}")
        print(f"Row limit: {limit}")
        
        # ADQL query for bright stars with good parallax measurements
        query = f"""
        SELECT TOP {limit}
            source_id,
            ra,
            dec,
            parallax,
            parallax_error,
            phot_g_mean_mag,
            bp_rp,
            pmra,
            pmdec
        FROM gaiadr3.gaia_source
        WHERE parallax IS NOT NULL
          AND parallax_error IS NOT NULL
          AND parallax > 0
          AND phot_g_mean_mag < {magnitude_limit}
        ORDER BY phot_g_mean_mag ASC
        """
        
        print(f"\nExecuting ADQL query...")
        try:
            job = Gaia.launch_job_async(query)
            results = job.get_results()
            print(f"✓ Retrieved {len(results)} stars from Gaia DR3")
            
            # Convert to list of dicts
            stars = []
            for row in results:
                stars.append({
                    'source_id': str(row['source_id']),
                    'ra': float(row['ra']),
                    'dec': float(row['dec']),
                    'parallax': float(row['parallax']),
                    'parallax_error': float(row['parallax_error']),
                    'magnitude_g': float(row['phot_g_mean_mag']),
                    'color_bp_rp': float(row['bp_rp']) if row['bp_rp'] is not None else None,
                    'pmra': float(row['pmra']) if row['pmra'] is not None else None,
                    'pmdec': float(row['pmdec']) if row['pmdec'] is not None else None
                })
            
            return stars
            
        except Exception as e:
            print(f"✗ Gaia query failed: {e}")
            sys.exit(1)
    
    def validate_and_adjudicate(self, stars: List[Dict]) -> List[Dict]:
        """
        Validate data and adjudicate epistemic status.
        
        INVARIANT I (LABELING): Enforced here!
        - All Gaia data is OBSERVED (direct measurement)
        - Reject any star without parallax_error (no error margin)
        
        Args:
            stars: Raw Gaia data
        
        Returns:
            Validated stars with epistemic status and provenance
        """
        print(f"\n{'='*60}")
        print("EPISTEMIC ADJUDICATION (Invariant I)")
        print(f"{'='*60}")
        
        validated = []
        rejected_count = 0
        
        for star in stars:
            # Labeling Check: Must have error margin
            if star['parallax_error'] is None or star['parallax_error'] <= 0:
                rejected_count += 1
                continue
            
            # Calculate distance from parallax (in parsecs)
            # Distance = 1000 / parallax_mas
            distance_pc = 1000.0 / star['parallax']
            
            # Build provenance JSONB
            provenance = {
                'source': self.GAIA_DR3_SOURCE,
                'doi': self.GAIA_DR3_DOI,
                'release_date': self.GAIA_DR3_RELEASE_DATE,
                'parallax_error_mas': star['parallax_error'],
                'parallax_over_error': star['parallax'] / star['parallax_error'],
                'gaia_source_id': star['source_id']
            }
            
            # Add validated star
            validated.append({
                'id': f"GaiaDR3_{star['source_id']}",
                'truth_label': 'OBSERVED',  # Invariant I: Explicit label
                'ra': star['ra'],
                'dec': star['dec'],
                'distance_pc': distance_pc,
                'parallax_mas': star['parallax'],
                'magnitude_g': star['magnitude_g'],
                'color_bp_rp': star['color_bp_rp'],
                'provenance': json.dumps(provenance)
            })
        
        print(f"✓ Validated: {len(validated)} stars")
        print(f"✗ Rejected: {rejected_count} stars (missing error margin)")
        print(f"  Pass rate: {len(validated) / len(stars) * 100:.1f}%")
        
        return validated
    
    def insert_to_db(self, stars: List[Dict]):
        """
        Insert validated stars into PostGIS database.
        
        Args:
            stars: Validated star data with epistemic labels
        """
        print(f"\n{'='*60}")
        print("DATABASE INSERTION")
        print(f"{'='*60}")
        
        # Prepare data for batch insert
        # Format: (id, truth_label, location, parallax, magnitude, color, provenance)
        values = []
        for star in stars:
            # Create PostGIS POINTZ (RA, Dec, Distance)
            # Note: PostGIS GEOGRAPHY uses (longitude, latitude, elevation)
            # We map: RA -> longitude, Dec -> latitude, Distance -> elevation
            location_wkt = f"SRID=4326;POINTZ({star['ra']} {star['dec']} {star['distance_pc']})"
            
            values.append((
                star['id'],
                star['truth_label'],
                location_wkt,
                star['parallax_mas'],
                star['magnitude_g'],
                star['color_bp_rp'],
                star['provenance']
            ))
        
        # Batch insert
        insert_query = """
            INSERT INTO cosmic_objects (
                id,
                truth_label,
                location,
                parallax_mas,
                magnitude_g,
                color_index_bp_rp,
                provenance
            ) VALUES %s
            ON CONFLICT (id) DO NOTHING
        """
        
        try:
            execute_values(
                self.cursor,
                insert_query,
                values,
                template="(%s, %s::epistemic_status_type, ST_GeographyFromText(%s), %s, %s, %s, %s::jsonb)"
            )
            self.conn.commit()
            print(f"✓ Inserted {len(stars)} stars into cosmic_objects table")
            
        except Exception as e:
            self.conn.rollback()
            print(f"✗ Database insertion failed: {e}")
            raise
    
    def print_statistics(self):
        """Print database statistics."""
        print(f"\n{'='*60}")
        print("DATABASE STATISTICS")
        print(f"{'='*60}")
        
        # Count by epistemic status
        self.cursor.execute("""
            SELECT truth_label, COUNT(*) 
            FROM cosmic_objects 
            GROUP BY truth_label
        """)
        
        for label, count in self.cursor.fetchall():
            print(f"  {label}: {count:,} objects")
        
        # Total count
        self.cursor.execute("SELECT COUNT(*) FROM cosmic_objects")
        total = self.cursor.fetchone()[0]
        print(f"  TOTAL: {total:,} objects")
    
    def close(self):
        """Close database connection."""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()


def main():
    parser = argparse.ArgumentParser(
        description="Ingest Gaia DR3 data into Epistemic Engine database",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
CONSTITUTION COMPLIANCE:
  - All Gaia data labeled as OBSERVED (Invariant I)
  - Stars without parallax_error are REJECTED
  - Provenance includes DOI, source, and error margins
  
EXAMPLES:
  # Ingest 100k brightest stars
  python ingest_gaia.py --limit 100000 --magnitude-limit 12.0
  
  # Test with small sample
  python ingest_gaia.py --limit 100 --test
  
  # Custom database connection
  python ingest_gaia.py --db-host localhost --db-name epistemic_engine
        """
    )
    
    parser.add_argument('--limit', type=int, default=100000,
                       help='Number of stars to fetch (default: 100000)')
    parser.add_argument('--magnitude-limit', type=float, default=12.0,
                       help='Magnitude cutoff (default: 12.0)')
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
    parser.add_argument('--test', action='store_true',
                       help='Test mode: limit to 100 stars')
    
    args = parser.parse_args()
    
    # Test mode override
    if args.test:
        args.limit = 100
        print("⚠️  TEST MODE: Limited to 100 stars\n")
    
    # Database configuration
    db_config = {
        'host': args.db_host,
        'port': args.db_port,
        'database': args.db_name,
        'user': args.db_user,
        'password': args.db_password
    }
    
    # Execute pipeline
    pipeline = GaiaIngestionPipeline(db_config)
    
    try:
        # 1. Connect to database
        pipeline.connect_db()
        
        # 2. Query Gaia
        stars = pipeline.query_gaia(
            limit=args.limit,
            magnitude_limit=args.magnitude_limit
        )
        
        # 3. Validate and adjudicate
        validated_stars = pipeline.validate_and_adjudicate(stars)
        
        # 4. Insert to database
        pipeline.insert_to_db(validated_stars)
        
        # 5. Print statistics
        pipeline.print_statistics()
        
        print(f"\n✓ Ingestion complete!")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Ingestion interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Fatal error: {e}")
        sys.exit(1)
    finally:
        pipeline.close()


if __name__ == '__main__':
    main()
