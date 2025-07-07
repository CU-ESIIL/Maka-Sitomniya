#!/usr/bin/env python
"""
OSM Data Summary Script

Provides summary statistics about the downloaded and converted OSM data
for the Black Hills region.
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Any
from collections import defaultdict, Counter

def analyze_geojson_file(file_path: Path) -> Dict[str, Any]:
    """
    Analyze a GeoJSON file and return summary statistics.
    
    Args:
        file_path: Path to GeoJSON file
        
    Returns:
        Dictionary with analysis results
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if data.get('type') != 'FeatureCollection':
            return {'error': 'Not a valid GeoJSON FeatureCollection'}
        
        features = data.get('features', [])
        
        # Count by geometry type
        geometry_counts = Counter()
        property_counts = defaultdict(Counter)
        
        for feature in features:
            if 'geometry' in feature and feature['geometry']:
                geom_type = feature['geometry']['type']
                geometry_counts[geom_type] += 1
                
                # Count properties/tags
                properties = feature.get('properties', {})
                for key, value in properties.items():
                    if key not in ['osm_id', 'osm_type']:
                        property_counts[key][str(value)] += 1
        
        # Get top tags
        top_tags = {}
        for tag, values in property_counts.items():
            if len(values) > 1:  # Only include tags with variety
                top_tags[tag] = dict(values.most_common(5))
        
        return {
            'file_size_mb': file_path.stat().st_size / (1024 * 1024),
            'feature_count': len(features),
            'geometry_types': dict(geometry_counts),
            'top_tags': top_tags,
            'metadata': data.get('metadata', {})
        }
        
    except Exception as e:
        return {'error': str(e)}

def main():
    """Generate summary of OSM data."""
    
    # Define data directory
    data_dir = Path('datacube/data/osm')
    geojson_dir = data_dir / 'geojson'
    
    if not geojson_dir.exists():
        print("No GeoJSON directory found. Please run the converter first.")
        return 1
    
    # Find all GeoJSON files
    geojson_files = list(geojson_dir.rglob('*.geojson'))
    
    if not geojson_files:
        print("No GeoJSON files found.")
        return 1
    
    print("Black Hills OSM Data Summary")
    print("=" * 40)
    print()
    
    total_features = 0
    total_size_mb = 0
    
    # Analyze each category
    categories = {}
    
    for file_path in geojson_files:
        # Determine category from parent directory
        category = file_path.parent.name
        
        analysis = analyze_geojson_file(file_path)
        
        if 'error' in analysis:
            print(f"Error analyzing {file_path}: {analysis['error']}")
            continue
        
        categories[category] = analysis
        total_features += analysis['feature_count']
        total_size_mb += analysis['file_size_mb']
    
    # Print overall summary
    print(f"Total Features: {total_features:,}")
    print(f"Total Size: {total_size_mb:.2f} MB")
    print(f"Categories: {len(categories)}")
    print()
    
    # Print category details
    for category, analysis in sorted(categories.items()):
        print(f"{category.upper()}")
        print("-" * len(category))
        print(f"  Features: {analysis['feature_count']:,}")
        print(f"  Size: {analysis['file_size_mb']:.2f} MB")
        print(f"  Geometry Types: {analysis['geometry_types']}")
        
        if analysis['top_tags']:
            print("  Top Tags:")
            for tag, values in list(analysis['top_tags'].items())[:3]:
                print(f"    {tag}: {dict(list(values.items())[:3])}")
        
        print()
    
    # Print some interesting statistics
    print("Data Quality Insights:")
    print("-" * 20)
    
    # Roads analysis
    if 'roads' in categories:
        roads = categories['roads']
        print(f"• Road network: {roads['feature_count']:,} segments")
        if 'highway' in roads['top_tags']:
            highway_types = roads['top_tags']['highway']
            print(f"  - Main highway types: {list(highway_types.keys())[:5]}")
    
    # Buildings analysis
    if 'buildings' in categories:
        buildings = categories['buildings']
        print(f"• Buildings: {buildings['feature_count']:,} structures")
        if 'building' in buildings['top_tags']:
            building_types = buildings['top_tags']['building']
            print(f"  - Building types: {list(building_types.keys())[:5]}")
    
    # Natural features
    if 'natural' in categories:
        natural = categories['natural']
        print(f"• Natural features: {natural['feature_count']:,} elements")
        if 'natural' in natural['top_tags']:
            natural_types = natural['top_tags']['natural']
            print(f"  - Natural types: {list(natural_types.keys())[:5]}")
    
    # Amenities
    if 'amenities' in categories:
        amenities = categories['amenities']
        print(f"• Amenities/POIs: {amenities['feature_count']:,} locations")
        if 'amenity' in amenities['top_tags']:
            amenity_types = amenities['top_tags']['amenity']
            print(f"  - Amenity types: {list(amenity_types.keys())[:5]}")
    
    print()
    print("Files location: datacube/data/osm/geojson/")
    print("Use these GeoJSON files with QGIS, Python geopandas, or other GIS tools.")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())