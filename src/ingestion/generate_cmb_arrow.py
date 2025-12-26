#!/usr/bin/env python3
"""
Generate CMB Velocity Vector Arrow
===================================

EPISTEMIC STATUS: L2 (SIMULATED) - Visual Aid
PURPOSE: Visualization of Milky Way's motion relative to CMB rest frame

This script generates a 3D arrow mesh (.obj format) to represent the
velocity vector of the Milky Way relative to the Cosmic Microwave Background.

PHYSICAL CONTEXT:
- CMB Dipole: Our motion relative to CMB creates a dipole anisotropy
- Velocity: ~369 km/s
- Direction: Towards constellation Leo (l ≈ 264°, b ≈ 48° in Galactic coords)

CONSTITUTION COMPLIANCE:
- Invariant of Labeling: Tagged as L2 (SIMULATED) - this is a visual aid,
  not direct data. The velocity is L0 (OBSERVED from CMB dipole), but the
  arrow representation is procedural.
"""

import numpy as np
import argparse
from pathlib import Path
from datetime import datetime


class ArrowMeshGenerator:
    """Generates a 3D arrow mesh for representing velocity vectors."""
    
    # CMB velocity parameters (Planck 2018 results)
    CMB_VELOCITY_KMS = 369.0  # km/s
    CMB_DIRECTION_L = 264.021  # Galactic longitude (degrees)
    CMB_DIRECTION_B = 48.253   # Galactic latitude (degrees)
    
    def __init__(self, length=1e20, shaft_radius=1e18, head_radius=3e18, head_length=3e19):
        """
        Initialize arrow generator.
        
        Args:
            length: Total arrow length in meters (default: 100,000 light-years)
            shaft_radius: Radius of arrow shaft
            head_radius: Radius of arrow cone base
            head_length: Length of arrow cone
        """
        self.length = length
        self.shaft_radius = shaft_radius
        self.head_radius = head_radius
        self.head_length = head_length
        
    def galactic_to_cartesian(self, l_deg, b_deg, r=1.0):
        """
        Convert Galactic coordinates to Cartesian (X, Y, Z).
        
        Args:
            l_deg: Galactic longitude in degrees
            b_deg: Galactic latitude in degrees
            r: Radial distance (default: 1.0 for unit vector)
        
        Returns:
            np.array: [x, y, z] Cartesian coordinates
        """
        l_rad = np.radians(l_deg)
        b_rad = np.radians(b_deg)
        
        x = r * np.cos(b_rad) * np.cos(l_rad)
        y = r * np.cos(b_rad) * np.sin(l_rad)
        z = r * np.sin(b_rad)
        
        return np.array([x, y, z])
    
    def generate_arrow_mesh(self, segments=32):
        """
        Generate arrow mesh geometry.
        
        Args:
            segments: Number of radial segments for cylinder/cone
        
        Returns:
            dict: Vertices, faces, and normals
        """
        vertices = []
        faces = []
        
        # Direction vector (normalized)
        direction = self.galactic_to_cartesian(
            self.CMB_DIRECTION_L,
            self.CMB_DIRECTION_B
        )
        direction = direction / np.linalg.norm(direction)
        
        # Create rotation matrix to align arrow with direction
        # Default arrow points along +Z axis, rotate to match direction
        z_axis = np.array([0, 0, 1])
        rotation_matrix = self._rotation_matrix_from_vectors(z_axis, direction)
        
        # Generate shaft (cylinder)
        shaft_length = self.length - self.head_length
        shaft_vertices, shaft_faces = self._generate_cylinder(
            radius=self.shaft_radius,
            height=shaft_length,
            segments=segments,
            offset=np.array([0, 0, 0])
        )
        
        # Generate head (cone)
        head_vertices, head_faces = self._generate_cone(
            radius=self.head_radius,
            height=self.head_length,
            segments=segments,
            offset=np.array([0, 0, shaft_length])
        )
        
        # Combine meshes
        vertices = shaft_vertices + head_vertices
        
        # Offset face indices for head
        offset_head_faces = [[f[0] + len(shaft_vertices), 
                             f[1] + len(shaft_vertices), 
                             f[2] + len(shaft_vertices)] 
                            for f in head_faces]
        faces = shaft_faces + offset_head_faces
        
        # Apply rotation to align with CMB direction
        vertices = [rotation_matrix @ v for v in vertices]
        
        return {
            'vertices': vertices,
            'faces': faces,
            'direction': direction,
            'metadata': self._generate_metadata()
        }
    
    def _generate_cylinder(self, radius, height, segments, offset):
        """Generate cylinder mesh."""
        vertices = []
        faces = []
        
        # Generate vertices
        for i in range(segments):
            angle = 2 * np.pi * i / segments
            x = radius * np.cos(angle)
            y = radius * np.sin(angle)
            
            # Bottom circle
            vertices.append(offset + np.array([x, y, 0]))
            # Top circle
            vertices.append(offset + np.array([x, y, height]))
        
        # Generate side faces
        for i in range(segments):
            next_i = (i + 1) % segments
            
            # Two triangles per quad
            v0 = 2 * i
            v1 = 2 * i + 1
            v2 = 2 * next_i + 1
            v3 = 2 * next_i
            
            faces.append([v0, v1, v2])
            faces.append([v0, v2, v3])
        
        # Bottom cap (optional - commented out for hollow cylinder)
        # center_bottom = len(vertices)
        # vertices.append(offset + np.array([0, 0, 0]))
        # for i in range(segments):
        #     next_i = (i + 1) % segments
        #     faces.append([center_bottom, 2 * i, 2 * next_i])
        
        # Top cap
        center_top = len(vertices)
        vertices.append(offset + np.array([0, 0, height]))
        for i in range(segments):
            next_i = (i + 1) % segments
            faces.append([center_top, 2 * next_i + 1, 2 * i + 1])
        
        return vertices, faces
    
    def _generate_cone(self, radius, height, segments, offset):
        """Generate cone mesh."""
        vertices = []
        faces = []
        
        # Base circle vertices
        for i in range(segments):
            angle = 2 * np.pi * i / segments
            x = radius * np.cos(angle)
            y = radius * np.sin(angle)
            vertices.append(offset + np.array([x, y, 0]))
        
        # Apex vertex
        apex_idx = len(vertices)
        vertices.append(offset + np.array([0, 0, height]))
        
        # Side faces
        for i in range(segments):
            next_i = (i + 1) % segments
            faces.append([i, next_i, apex_idx])
        
        # Base (optional - commented out for hollow cone)
        # center_base = len(vertices)
        # vertices.append(offset + np.array([0, 0, 0]))
        # for i in range(segments):
        #     next_i = (i + 1) % segments
        #     faces.append([center_base, next_i, i])
        
        return vertices, faces
    
    def _rotation_matrix_from_vectors(self, vec1, vec2):
        """
        Create rotation matrix to rotate vec1 to vec2.
        
        Using Rodrigues' rotation formula.
        """
        a = vec1 / np.linalg.norm(vec1)
        b = vec2 / np.linalg.norm(vec2)
        
        v = np.cross(a, b)
        c = np.dot(a, b)
        
        if np.allclose(c, -1):
            # Vectors are opposite - return 180° rotation
            return -np.eye(3)
        
        s = np.linalg.norm(v)
        
        if s < 1e-10:
            # Vectors are already aligned
            return np.eye(3)
        
        # Skew-symmetric cross-product matrix
        vx = np.array([
            [0, -v[2], v[1]],
            [v[2], 0, -v[0]],
            [-v[1], v[0], 0]
        ])
        
        R = np.eye(3) + vx + (vx @ vx) * ((1 - c) / (s ** 2))
        
        return R
    
    def _generate_metadata(self):
        """Generate provenance metadata."""
        return {
            'epistemic_status': 'L2',
            'epistemic_label': 'SIMULATED',
            'note': 'Visual aid - arrow represents L0 CMB velocity data',
            'cmb_velocity_kms': self.CMB_VELOCITY_KMS,
            'cmb_direction_l': self.CMB_DIRECTION_L,
            'cmb_direction_b': self.CMB_DIRECTION_B,
            'source': 'Planck 2018 CMB dipole measurements',
            'reference_frame': 'CMB Rest Frame',
            'generation_date': datetime.now().isoformat()
        }
    
    def export_to_obj(self, output_path, mesh_data):
        """
        Export mesh to Wavefront OBJ format.
        
        Args:
            output_path: Path to output .obj file
            mesh_data: Dictionary from generate_arrow_mesh()
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w') as f:
            # Header
            f.write("# CMB Velocity Vector Arrow\n")
            f.write(f"# EPISTEMIC STATUS: {mesh_data['metadata']['epistemic_status']} ({mesh_data['metadata']['epistemic_label']})\n")
            f.write(f"# NOTE: {mesh_data['metadata']['note']}\n")
            f.write(f"# CMB Velocity: {mesh_data['metadata']['cmb_velocity_kms']} km/s\n")
            f.write(f"# Direction (Galactic): l={mesh_data['metadata']['cmb_direction_l']}°, b={mesh_data['metadata']['cmb_direction_b']}°\n")
            f.write(f"# SOURCE: {mesh_data['metadata']['source']}\n")
            f.write(f"# Generated: {mesh_data['metadata']['generation_date']}\n")
            f.write("#\n")
            
            # Vertices
            for v in mesh_data['vertices']:
                f.write(f"v {v[0]:.6e} {v[1]:.6e} {v[2]:.6e}\n")
            
            # Faces (OBJ indices start at 1, not 0)
            for face in mesh_data['faces']:
                f.write(f"f {face[0]+1} {face[1]+1} {face[2]+1}\n")
        
        print(f"✓ Exported mesh with {len(mesh_data['vertices'])} vertices and {len(mesh_data['faces'])} faces to {output_path}")
    
    def print_statistics(self, mesh_data):
        """Print summary statistics."""
        print("\n" + "="*60)
        print("CMB VELOCITY VECTOR ARROW - GENERATION SUMMARY")
        print("="*60)
        print(f"\nEPISTEMIC STATUS: {mesh_data['metadata']['epistemic_status']} ({mesh_data['metadata']['epistemic_label']})")
        print(f"NOTE: {mesh_data['metadata']['note']}")
        print(f"\nPHYSICAL DATA (L0 - OBSERVED):")
        print(f"  CMB Velocity: {mesh_data['metadata']['cmb_velocity_kms']} km/s")
        print(f"  Direction (Galactic): l = {mesh_data['metadata']['cmb_direction_l']}° (longitude)")
        print(f"                       b = {mesh_data['metadata']['cmb_direction_b']}° (latitude)")
        print(f"  Direction (Constellation): Towards Leo")
        print(f"  Source: {mesh_data['metadata']['source']}")
        print(f"\nARROW GEOMETRY (L2 - SIMULATED):")
        print(f"  Total length: {self.length:.2e} m (~{self.length / 9.461e15:.0f} light-years)")
        print(f"  Shaft radius: {self.shaft_radius:.2e} m")
        print(f"  Head radius: {self.head_radius:.2e} m")
        print(f"  Head length: {self.head_length:.2e} m")
        print(f"\nMESH STATISTICS:")
        print(f"  Vertices: {len(mesh_data['vertices'])}")
        print(f"  Faces: {len(mesh_data['faces'])}")
        print(f"  Direction vector: [{mesh_data['direction'][0]:.6f}, {mesh_data['direction'][1]:.6f}, {mesh_data['direction'][2]:.6f}]")
        print("="*60 + "\n")


def main():
    parser = argparse.ArgumentParser(
        description="Generate CMB velocity vector arrow mesh (L2 - SIMULATED visual aid for L0 data)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
EPISTEMIC COMPLIANCE:
  The CMB velocity (369 km/s towards Leo) is L0 (OBSERVED).
  The arrow mesh is L2 (SIMULATED) - a visual aid only.
  
  This distinction is critical: we're visualizing real data, but
  the arrow itself is procedural geometry.
  
EXAMPLES:
  # Generate default arrow
  python generate_cmb_arrow.py
  
  # Generate larger arrow with more detail
  python generate_cmb_arrow.py --length 2e20 --segments 64
  
  # Output to custom directory
  python generate_cmb_arrow.py --output-dir ../../data/vectors
        """
    )
    
    parser.add_argument(
        '--length',
        type=float,
        default=1e20,
        help='Arrow length in meters (default: 1e20 = ~10,000 light-years)'
    )
    
    parser.add_argument(
        '--segments',
        type=int,
        default=32,
        help='Radial segments for cylinder/cone (default: 32)'
    )
    
    parser.add_argument(
        '--output-dir',
        type=str,
        default='../../data/cmb_vector',
        help='Output directory (default: ../../data/cmb_vector)'
    )
    
    args = parser.parse_args()
    
    # Generate arrow mesh
    print("\nGenerating CMB velocity vector arrow...")
    generator = ArrowMeshGenerator(length=args.length)
    
    mesh_data = generator.generate_arrow_mesh(segments=args.segments)
    
    # Print statistics
    generator.print_statistics(mesh_data)
    
    # Export mesh
    output_path = Path(args.output_dir) / 'cmb_velocity_arrow.obj'
    generator.export_to_obj(output_path, mesh_data)
    
    print(f"✓ CMB velocity arrow generation complete!")
    print(f"✓ Output file: {output_path.absolute()}\n")


if __name__ == '__main__':
    main()
