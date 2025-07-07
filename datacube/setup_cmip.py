"""
Setup script to configure CMIP module imports for notebooks and scripts.

Run this once to set up the CMIP modules for easy importing.
"""

import sys
import os
from pathlib import Path

def setup_cmip_imports():
    """Set up CMIP module imports."""
    
    # Get the datacube directory
    datacube_dir = Path(__file__).parent.resolve()
    cmip_dir = datacube_dir / 'cmip'
    
    print(f"Setting up CMIP imports from: {cmip_dir}")
    
    # Add paths to sys.path if not already there
    paths_to_add = [
        str(datacube_dir),
        str(cmip_dir),
        str(cmip_dir / 'download'),
        str(cmip_dir / 'process'),
        str(cmip_dir / 'visualize'),
        str(cmip_dir / 'datacube'),
    ]
    
    for path in paths_to_add:
        if path not in sys.path:
            sys.path.insert(0, path)
    
    # Change to datacube directory
    os.chdir(datacube_dir)
    
    print("✅ CMIP import paths configured")
    print(f"✅ Working directory set to: {os.getcwd()}")
    
    # Test imports
    try:
        from cmip.download.sources import BLACK_HILLS_BBOX
        print(f"✅ Test import successful: Black Hills at {BLACK_HILLS_BBOX.north}°N")
        return True
    except ImportError as e:
        print(f"❌ Test import failed: {e}")
        return False

if __name__ == "__main__":
    setup_cmip_imports()