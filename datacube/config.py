#!/usr/bin/env python
"""
Configuration settings for the datacube implementation.

This module contains shared configuration parameters, geographic regions, and constants
used across the datacube processing pipeline.
"""

# Directory configuration
import os
# Base directory is the directory where this script is located
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
OUTPUTS_DIR = os.path.join(BASE_DIR, "data/processed")

# Default datacube parameters
DEFAULT_SPATIAL_RESOLUTION = 30  # meters
DEFAULT_TEMPORAL_RESOLUTION = "ME"  # Month end
DEFAULT_CRS = "EPSG:4326"  # WGS84 projection

# Standard aggregation methods
DEFAULT_NUMERIC_AGGREGATION = "mean"
DEFAULT_CATEGORICAL_AGGREGATION = "mode"

# Region definitions

# Black Hills region (Web Mercator projection coordinates in meters)
# To use this with lat/lon coordinates, it needs to be reprojected
BLACK_HILLS_BBOX_MERCATOR = {
    "name": "Black Hills",
    "description": "Black Hills region in South Dakota",
    "top": 5589386.763400,      # North coordinate (m)
    "bottom": 5353897.225000,   # South coordinate (m)
    "left": -11657352.348600,   # West coordinate (m)
    "right": -11499753.118600,  # East coordinate (m)
    "projection": "EPSG:3857"   # Web Mercator projection
}

# Reproject the Web Mercator coordinates to WGS84 (approximate conversion for convenience)
# Values derived from reprojection of the Web Mercator coordinates
BLACK_HILLS_BBOX_WGS84 = {
    "name": "Black Hills",
    "description": "Black Hills region in South Dakota (WGS84 coordinates)",
    "north": 44.652,  # North latitude
    "south": 43.480,  # South latitude
    "west": -104.705, # West longitude
    "east": -103.264, # East longitude
    "projection": "EPSG:4326"  # WGS84 projection
}

# Format the WGS84 bounding box as a string for convenient use with libraries
# Format is "west south east north" (minx miny maxx maxy)
BLACK_HILLS_BBOX_STRING = f"{BLACK_HILLS_BBOX_WGS84['west']} {BLACK_HILLS_BBOX_WGS84['south']} {BLACK_HILLS_BBOX_WGS84['east']} {BLACK_HILLS_BBOX_WGS84['north']}"

# Data source configurations
LANDFIRE_CONFIG = {
    "version": "220",  # 2020 version 
    "layers": {
        "evt": f"{220}EVT",  # Existing Vegetation Type
        "evc": f"{220}EVC",  # Existing Vegetation Cover
        "evh": f"{220}EVH"   # Existing Vegetation Height
    },
    "data_dir": os.path.join(DATA_DIR, "landfire")
}

# CMIP climate model configurations
CMIP_CONFIG = {
    "models": ["CCSM4"],
    "scenarios": ["rcp45", "rcp85"],
    "variables": ["huss"],  # Specific humidity
    "years": "2021_2025",
    "region": "CONUS",
    "frequency": "monthly",
    "data_dir": DATA_DIR
}

if __name__ == "__main__":
    # Print configuration when run directly
    print("Datacube Configuration")
    print("====================")
    print(f"Black Hills Bounding Box (WGS84): {BLACK_HILLS_BBOX_STRING}")
    print(f"Default Spatial Resolution: {DEFAULT_SPATIAL_RESOLUTION} meters")
    print(f"Default Temporal Resolution: {DEFAULT_TEMPORAL_RESOLUTION}")
    print(f"LANDFIRE Version: {LANDFIRE_CONFIG['version']}")
    print(f"LANDFIRE Layers: {list(LANDFIRE_CONFIG['layers'].keys())}")
    print(f"CMIP Models: {CMIP_CONFIG['models']}")
    print(f"CMIP Scenarios: {CMIP_CONFIG['scenarios']}")