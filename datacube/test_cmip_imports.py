#!/usr/bin/env python
"""
Test script to verify CMIP module imports work correctly.
Run this from the datacube directory to test the imports.
"""

import sys
import os
from pathlib import Path

def test_imports():
    """Test importing all CMIP modules."""
    print("Testing CMIP module imports...")
    print(f"Current working directory: {os.getcwd()}")
    print(f"Python path: {sys.path[:3]}...")  # Show first 3 entries
    
    try:
        # Method 1: Direct imports (when run from datacube directory)
        print("\n=== Method 1: Direct imports ===")
        from cmip.download.fetcher import MACAfetcher, download_black_hills_subset
        from cmip.download.sources import Variable, ClimateModel, Scenario, BLACK_HILLS_BBOX
        from cmip.process.loader import CMIPLoader
        from cmip.process.cleaner import ClimateValidator, ClimateCleaner
        from cmip.process.resampler import ClimateResampler, ResampleMethod
        from cmip.visualize.maps import ClimateMapPlotter
        from cmip.visualize.timeseries import ClimateTimeSeriesPlotter
        from cmip.datacube.builder import build_black_hills_datacube
        
        print("✅ All direct imports successful!")
        
        # Test basic functionality
        print(f"✅ Black Hills bbox: {BLACK_HILLS_BBOX.north}°N, {BLACK_HILLS_BBOX.south}°S")
        print(f"✅ Available variables: {[v.value for v in list(Variable)[:3]]}...")
        print(f"✅ Available models: {[m.value for m in list(ClimateModel)[:3]]}...")
        
        return True
        
    except ImportError as e:
        print(f"❌ Direct imports failed: {e}")
        
        # Method 2: Add paths and try again
        print("\n=== Method 2: Path-based imports ===")
        try:
            cmip_path = Path('cmip').resolve()
            sys.path.insert(0, str(cmip_path))
            sys.path.insert(0, str(cmip_path / 'download'))
            sys.path.insert(0, str(cmip_path / 'process'))
            sys.path.insert(0, str(cmip_path / 'visualize'))
            sys.path.insert(0, str(cmip_path / 'datacube'))
            
            from fetcher import MACAfetcher, download_black_hills_subset
            from sources import Variable, ClimateModel, Scenario, BLACK_HILLS_BBOX
            from loader import CMIPLoader
            from cleaner import ClimateValidator, ClimateCleaner
            from resampler import ClimateResampler, ResampleMethod
            from maps import ClimateMapPlotter
            from timeseries import ClimateTimeSeriesPlotter
            from builder import build_black_hills_datacube
            
            print("✅ Path-based imports successful!")
            print(f"✅ Black Hills bbox: {BLACK_HILLS_BBOX.north}°N, {BLACK_HILLS_BBOX.south}°S")
            
            return True
            
        except ImportError as e2:
            print(f"❌ Path-based imports also failed: {e2}")
            return False


def test_basic_functionality():
    """Test basic functionality of imported modules."""
    print("\n=== Testing Basic Functionality ===")
    
    try:
        # Test fetcher initialization
        fetcher = MACAfetcher(data_dir="./test_data")
        print("✅ MACAfetcher initialized")
        
        # Test loader
        loader = CMIPLoader()
        print("✅ CMIPLoader initialized")
        
        # Test validator
        validator = ClimateValidator()
        print("✅ ClimateValidator initialized")
        
        # Test cleaner
        cleaner = ClimateCleaner()
        print("✅ ClimateCleaner initialized")
        
        # Test resampler
        resampler = ClimateResampler()
        print("✅ ClimateResampler initialized")
        
        # Test plotters
        map_plotter = ClimateMapPlotter()
        ts_plotter = ClimateTimeSeriesPlotter()
        print("✅ Plotters initialized")
        
        print("✅ All basic functionality tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Functionality test failed: {e}")
        return False


if __name__ == "__main__":
    print("CMIP Module Import Test")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not Path('cmip').exists():
        print("❌ Error: cmip directory not found!")
        print("Please run this script from the datacube directory.")
        sys.exit(1)
    
    # Test imports
    import_success = test_imports()
    
    if import_success:
        # Test functionality
        func_success = test_basic_functionality()
        
        if func_success:
            print("\n🎉 All tests passed! CMIP modules are working correctly.")
        else:
            print("\n⚠️  Imports work but functionality test failed.")
    else:
        print("\n❌ Import tests failed. Check your Python environment.")
        print("\nTroubleshooting tips:")
        print("1. Make sure you're running from the datacube directory")
        print("2. Check that all CMIP module files exist")
        print("3. Install required dependencies: pip install xarray netcdf4 cftime cartopy")
    
    print("\n" + "=" * 50)