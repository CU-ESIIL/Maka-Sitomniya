#!/usr/bin/env python
"""
Setup script for Google Earth Engine access to MACA v2 data.

This script helps set up Google Earth Engine for accessing MACA v2 climate data
since the USGS THREDDS server was retired in April 2024.
"""

import subprocess
import sys
import os
from pathlib import Path

def check_package_installed(package_name):
    """Check if a Python package is installed."""
    try:
        __import__(package_name)
        return True
    except ImportError:
        return False

def install_package(package_name):
    """Install a Python package using pip."""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
        return True
    except subprocess.CalledProcessError:
        return False

def setup_gee_packages():
    """Install required packages for Google Earth Engine."""
    print("🔧 Setting up Google Earth Engine packages...")
    
    required_packages = [
        "earthengine-api",
        "geemap", 
        "folium",
        "ipyleaflet"
    ]
    
    for package in required_packages:
        if check_package_installed(package.replace("-", "_")):
            print(f"✅ {package} already installed")
        else:
            print(f"📦 Installing {package}...")
            if install_package(package):
                print(f"✅ {package} installed successfully")
            else:
                print(f"❌ Failed to install {package}")
                return False
    
    return True

def authenticate_gee():
    """Help user authenticate with Google Earth Engine."""
    print("\n🔐 Google Earth Engine Authentication")
    print("=" * 50)
    
    try:
        import ee
        
        # Try to initialize without authentication
        try:
            ee.Initialize()
            print("✅ Already authenticated with Google Earth Engine!")
            return True
        except:
            pass
        
        print("You need to authenticate with Google Earth Engine.")
        print("\nOptions:")
        print("1. Run: earthengine authenticate")
        print("2. Or use service account authentication")
        print("\nFor option 1:")
        
        response = input("Would you like to run 'earthengine authenticate' now? (y/n): ")
        
        if response.lower() in ['y', 'yes']:
            try:
                subprocess.run(["earthengine", "authenticate"], check=True)
                print("✅ Authentication completed!")
                
                # Test initialization
                ee.Initialize()
                print("✅ Google Earth Engine initialized successfully!")
                return True
                
            except subprocess.CalledProcessError:
                print("❌ Authentication failed")
                print("Try running 'earthengine authenticate' manually")
                return False
            except Exception as e:
                print(f"❌ Initialization failed: {e}")
                return False
        else:
            print("Please run 'earthengine authenticate' manually")
            return False
            
    except ImportError:
        print("❌ earthengine-api not installed")
        return False

def test_maca_access():
    """Test access to MACA v2 data in Google Earth Engine."""
    print("\n🧪 Testing MACA v2 Data Access")
    print("=" * 40)
    
    try:
        import ee
        
        # Initialize Earth Engine
        ee.Initialize()
        
        # Try to access MACA collection
        collection = ee.ImageCollection("IDAHO_EPSCOR/MACAv2_METDATA")
        
        # Get basic info
        size = collection.size()
        first_image = ee.Image(collection.first())
        
        print(f"✅ MACA v2 collection accessible!")
        print(f"   Total images: {size.getInfo()}")
        print(f"   First image bands: {first_image.bandNames().getInfo()}")
        
        # Test filtering
        filtered = collection.filter(ee.Filter.date('2020-01-01', '2020-02-01'))
        filtered_size = filtered.size()
        print(f"   Sample filter (Jan 2020): {filtered_size.getInfo()} images")
        
        return True
        
    except Exception as e:
        print(f"❌ MACA data access failed: {e}")
        print("\nPossible issues:")
        print("- Authentication not completed")
        print("- No internet connection") 
        print("- Dataset permissions")
        return False

def main():
    """Main setup function."""
    print("🌍 Google Earth Engine Setup for MACA v2 Climate Data")
    print("=" * 60)
    print("\nBackground:")
    print("The USGS THREDDS server was retired in April 2024.")
    print("MACA v2 climate data is now best accessed via Google Earth Engine.")
    print("")
    
    # Step 1: Install packages
    if not setup_gee_packages():
        print("❌ Package installation failed")
        return False
    
    # Step 2: Authentication
    if not authenticate_gee():
        print("❌ Authentication failed")
        print("\nManual steps:")
        print("1. Install Earth Engine CLI: pip install earthengine-api")
        print("2. Authenticate: earthengine authenticate")
        print("3. Follow the browser instructions")
        return False
    
    # Step 3: Test data access
    if not test_maca_access():
        print("❌ Data access test failed")
        return False
    
    print("\n🎉 Setup Complete!")
    print("=" * 30)
    print("You can now access MACA v2 climate data via Google Earth Engine.")
    print("\nNext steps:")
    print("1. Use the gee_fetcher.py module")
    print("2. Run the updated cmip_simple.ipynb notebook")
    print("3. Explore Google Earth Engine tutorials")
    
    return True

if __name__ == "__main__":
    success = main()
    
    if success:
        print("\n✅ All setup steps completed successfully!")
    else:
        print("\n❌ Setup incomplete - see messages above")
        print("\nFor help:")
        print("- Google Earth Engine docs: https://developers.google.com/earth-engine")
        print("- MACA dataset: https://developers.google.com/earth-engine/datasets/catalog/IDAHO_EPSCOR_MACAv2_METDATA")