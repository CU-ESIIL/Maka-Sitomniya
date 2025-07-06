#!/usr/bin/env python3
"""
Manual CMIP/MACA data download script.

This script provides multiple methods for manually downloading MACA v2 climate data
since the original USGS THREDDS server was retired.
"""

import os
import sys
import requests
from pathlib import Path
from datetime import datetime

def download_from_url(url, output_path, chunk_size=8192):
    """Download a file from a URL with progress indication."""
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        total_size = int(response.headers.get('content-length', 0))
        
        with open(output_path, 'wb') as f:
            downloaded = 0
            for chunk in response.iter_content(chunk_size=chunk_size):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    
                    if total_size > 0:
                        percent = (downloaded / total_size) * 100
                        print(f"\rDownloading: {percent:.1f}%", end='', flush=True)
        
        print(f"\n✅ Downloaded: {output_path}")
        return True
        
    except Exception as e:
        print(f"\n❌ Download failed: {e}")
        return False

def list_alternative_sources():
    """List alternative data sources for MACA v2."""
    print("🌐 Alternative MACA v2 Data Sources:")
    print("=" * 50)
    
    sources = [
        {
            "name": "Google Earth Engine",
            "url": "https://developers.google.com/earth-engine/datasets/catalog/IDAHO_EPSCOR_MACAv2_METDATA",
            "method": "API/Code Editor",
            "notes": "Primary source - requires authentication"
        },
        {
            "name": "Climate Data Online (NOAA)",
            "url": "https://www.ncdc.noaa.gov/data-access",
            "method": "Web interface",
            "notes": "Search for 'MACA' or 'downscaled climate'"
        },
        {
            "name": "NASA Giovanni",
            "url": "https://giovanni.gsfc.nasa.gov/giovanni/",
            "method": "Web interface",
            "notes": "Interactive analysis and download"
        },
        {
            "name": "North Carolina Climate Office",
            "url": "https://climate.ncsu.edu/data/",
            "method": "THREDDS server",
            "notes": "MACAv2-LIVNEH variant"
        },
        {
            "name": "University of Idaho",
            "url": "https://www.uidaho.edu/research/climate-science",
            "method": "Check their data portal",
            "notes": "Original MACA developers"
        }
    ]
    
    for i, source in enumerate(sources, 1):
        print(f"\n{i}. {source['name']}")
        print(f"   URL: {source['url']}")
        print(f"   Method: {source['method']}")
        print(f"   Notes: {source['notes']}")

def setup_gee_download():
    """Set up Google Earth Engine for downloading."""
    print("\n🔧 Setting up Google Earth Engine Download:")
    print("=" * 50)
    
    steps = [
        "1. Sign up at https://earthengine.google.com/",
        "2. Install Python API: pip install earthengine-api",
        "3. Authenticate: earthengine authenticate",
        "4. Use the dataset: IDAHO_EPSCOR/MACAv2_METDATA"
    ]
    
    for step in steps:
        print(step)
    
    print("\n📝 Example Python code:")
    print("""
import ee
ee.Initialize()

# Load MACA collection
collection = ee.ImageCollection('IDAHO_EPSCOR/MACAv2_METDATA')

# Filter for your needs
filtered = collection.filterDate('2020-01-01', '2025-12-31') \\
                   .filter(ee.Filter.eq('model', 'GFDL-ESM2M')) \\
                   .filter(ee.Filter.eq('scenario', 'rcp45'))

# Export to Google Drive
task = ee.batch.Export.image.toDrive(
    image=filtered.first(),
    description='MACA_manual_download',
    folder='EarthEngine',
    scale=4000,
    region=ee.Geometry.Rectangle([-105, 43, -103, 45])  # Black Hills
)
task.start()
print('Download task started - check Google Drive')
""")

def check_gee_status():
    """Check if Google Earth Engine is available."""
    try:
        import ee
        ee.Initialize()
        print("✅ Google Earth Engine is ready!")
        return True
    except ImportError:
        print("❌ Google Earth Engine not installed")
        print("Install with: pip install earthengine-api")
        return False
    except Exception as e:
        print(f"❌ Google Earth Engine not authenticated: {e}")
        print("Run: earthengine authenticate")
        return False

def main():
    """Main function for manual download interface."""
    print("🌡️  Manual CMIP/MACA Data Download Tool")
    print("=" * 50)
    
    print("\nAvailable options:")
    print("1. List alternative data sources")
    print("2. Set up Google Earth Engine download")
    print("3. Check Google Earth Engine status")
    print("4. Exit")
    
    while True:
        choice = input("\nEnter your choice (1-4): ").strip()
        
        if choice == '1':
            list_alternative_sources()
        elif choice == '2':
            setup_gee_download()
        elif choice == '3':
            check_gee_status()
        elif choice == '4':
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please enter 1-4.")

if __name__ == "__main__":
    main()