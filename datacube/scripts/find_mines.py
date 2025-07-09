#!/usr/bin/env python
"""
Mining Features Extractor for Black Hills OSM Data

Identifies and extracts mining-related features from the converted OSM GeoJSON data.
This includes active mines, historical mining sites, quarries, and mining-related infrastructure.
"""

import json
import sys
import re
from pathlib import Path
from typing import Dict, List, Set, Any
from collections import defaultdict

class MiningFeatureExtractor:
    """Extract mining-related features from OSM GeoJSON data."""
    
    def __init__(self):
        """Initialize the mining feature extractor."""
        # Define mining-related keywords and tags
        self.mining_keywords = {
            'mine', 'mining', 'quarry', 'pit', 'shaft', 'adit', 'tunnel',
            'excavation', 'extraction', 'ore', 'coal', 'gold', 'silver',
            'copper', 'iron', 'gravel', 'sand', 'stone', 'mineral',
            'tailings', 'slag', 'spoil', 'claim', 'prospecting'
        }
        
        # Mining-specific OSM tags
        self.mining_tags = {
            'man_made': ['mineshaft', 'adit', 'mining_site', 'quarry'],
            'industrial': ['mine', 'quarry', 'mining'],
            'landuse': ['quarry', 'mining'],
            'natural': ['cliff', 'scree'],  # Often associated with mining
            'historic': ['mine', 'mining_site', 'quarry'],
            'ruins': ['mine', 'mining'],
            'tourism': ['mine', 'mining_site']
        }
        
        # Geology-related tags that might indicate mining potential
        self.geology_tags = {
            'geological', 'geology', 'mineral', 'outcrop', 'vein',
            'deposit', 'formation', 'pegmatite', 'quartz'
        }
    
    def _contains_mining_keywords(self, text: str) -> bool:
        """Check if text contains mining-related keywords."""
        if not text:
            return False
        
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in self.mining_keywords)
    
    def _is_mining_feature(self, properties: Dict[str, Any]) -> Dict[str, Any]:
        """
        Determine if a feature is mining-related and classify it.
        
        Args:
            properties: Feature properties dictionary
            
        Returns:
            Dictionary with mining classification info
        """
        mining_info = {
            'is_mining': False,
            'mining_type': None,
            'confidence': 'low',
            'evidence': []
        }
        
        # Check direct mining tags
        for tag, values in self.mining_tags.items():
            if tag in properties:
                prop_value = str(properties[tag]).lower()
                if prop_value in values:
                    mining_info['is_mining'] = True
                    mining_info['mining_type'] = f"{tag}:{prop_value}"
                    mining_info['confidence'] = 'high'
                    mining_info['evidence'].append(f"Direct tag: {tag}={prop_value}")
        
        # Check name and description fields
        text_fields = ['name', 'description', 'alt_name', 'official_name']
        for field in text_fields:
            if field in properties:
                if self._contains_mining_keywords(properties[field]):
                    mining_info['is_mining'] = True
                    mining_info['evidence'].append(f"Keyword in {field}: {properties[field]}")
                    if mining_info['confidence'] == 'low':
                        mining_info['confidence'] = 'medium'
        
        # Check address fields (e.g., "Miners Avenue")
        address_fields = ['addr:street', 'addr:city']
        for field in address_fields:
            if field in properties:
                if self._contains_mining_keywords(properties[field]):
                    mining_info['is_mining'] = True
                    mining_info['evidence'].append(f"Address keyword in {field}: {properties[field]}")
        
        # Check for geological features that might indicate mining
        for field, value in properties.items():
            if isinstance(value, str):
                value_lower = value.lower()
                if any(geo_term in value_lower for geo_term in self.geology_tags):
                    mining_info['evidence'].append(f"Geological term in {field}: {value}")
        
        return mining_info
    
    def extract_mining_features(self, geojson_file: Path) -> List[Dict[str, Any]]:
        """
        Extract mining features from a GeoJSON file.
        
        Args:
            geojson_file: Path to GeoJSON file
            
        Returns:
            List of mining-related features
        """
        mining_features = []
        
        try:
            with open(geojson_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if data.get('type') != 'FeatureCollection':
                return mining_features
            
            for feature in data.get('features', []):
                properties = feature.get('properties', {})
                mining_info = self._is_mining_feature(properties)
                
                if mining_info['is_mining']:
                    mining_feature = {
                        'source_file': geojson_file.name,
                        'geometry': feature.get('geometry'),
                        'properties': properties,
                        'mining_info': mining_info
                    }
                    mining_features.append(mining_feature)
        
        except Exception as e:
            print(f"Error processing {geojson_file}: {e}")
        
        return mining_features
    
    def analyze_all_files(self, geojson_dir: Path) -> Dict[str, Any]:
        """
        Analyze all GeoJSON files for mining features.
        
        Args:
            geojson_dir: Directory containing GeoJSON files
            
        Returns:
            Dictionary with analysis results
        """
        all_mining_features = []
        files_processed = 0
        
        # Process all GeoJSON files
        for geojson_file in geojson_dir.rglob('*.geojson'):
            features = self.extract_mining_features(geojson_file)
            all_mining_features.extend(features)
            files_processed += 1
        
        # Categorize features
        categories = defaultdict(list)
        confidence_levels = defaultdict(int)
        
        for feature in all_mining_features:
            mining_info = feature['mining_info']
            
            # Categorize by type
            if mining_info['mining_type']:
                categories[mining_info['mining_type']].append(feature)
            else:
                categories['general'].append(feature)
            
            # Count confidence levels
            confidence_levels[mining_info['confidence']] += 1
        
        return {
            'total_features': len(all_mining_features),
            'files_processed': files_processed,
            'categories': dict(categories),
            'confidence_levels': dict(confidence_levels),
            'all_features': all_mining_features
        }
    
    def save_mining_features(self, analysis_results: Dict[str, Any], output_file: Path):
        """
        Save mining features to a GeoJSON file.
        
        Args:
            analysis_results: Results from analyze_all_files
            output_file: Path to output GeoJSON file
        """
        features = []
        
        for feature in analysis_results['all_features']:
            geojson_feature = {
                'type': 'Feature',
                'geometry': feature['geometry'],
                'properties': {
                    **feature['properties'],
                    'mining_type': feature['mining_info']['mining_type'],
                    'mining_confidence': feature['mining_info']['confidence'],
                    'mining_evidence': '; '.join(feature['mining_info']['evidence']),
                    'source_file': feature['source_file']
                }
            }
            features.append(geojson_feature)
        
        geojson_output = {
            'type': 'FeatureCollection',
            'features': features,
            'metadata': {
                'total_features': len(features),
                'extraction_date': str(Path().absolute()),
                'description': 'Mining-related features extracted from Black Hills OSM data'
            }
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(geojson_output, f, indent=2, ensure_ascii=False)
        
        print(f"Mining features saved to: {output_file}")


def main():
    """Main function to find and analyze mining features."""
    
    # Define paths
    geojson_dir = Path('datacube/data/osm/geojson')
    output_dir = Path('datacube/data/osm')
    
    if not geojson_dir.exists():
        print("GeoJSON directory not found. Please run the OSM converter first.")
        return 1
    
    # Create extractor
    extractor = MiningFeatureExtractor()
    
    # Analyze all files
    print("Analyzing OSM data for mining features...")
    results = extractor.analyze_all_files(geojson_dir)
    
    # Print summary
    print(f"\nMining Features Analysis - Black Hills Region")
    print("=" * 50)
    print(f"Files processed: {results['files_processed']}")
    print(f"Total mining features found: {results['total_features']}")
    print()
    
    # Print confidence levels
    print("Confidence Levels:")
    for level, count in results['confidence_levels'].items():
        print(f"  {level.title()}: {count} features")
    print()
    
    # Print categories
    print("Mining Feature Categories:")
    for category, features in results['categories'].items():
        print(f"  {category}: {len(features)} features")
        
        # Show examples
        if len(features) > 0:
            example_names = []
            for feature in features[:3]:  # Show first 3 examples
                name = feature['properties'].get('name', 'Unnamed')
                example_names.append(name)
            if example_names:
                print(f"    Examples: {', '.join(example_names)}")
    print()
    
    # Print detailed high-confidence features
    print("High-Confidence Mining Features:")
    print("-" * 30)
    high_conf_features = [f for f in results['all_features'] 
                         if f['mining_info']['confidence'] == 'high']
    
    for feature in high_conf_features[:10]:  # Show first 10
        props = feature['properties']
        name = props.get('name', 'Unnamed')
        mining_type = feature['mining_info']['mining_type']
        evidence = feature['mining_info']['evidence'][0] if feature['mining_info']['evidence'] else 'No evidence'
        
        print(f"• {name}")
        print(f"  Type: {mining_type}")
        print(f"  Evidence: {evidence}")
        if 'geometry' in feature and 'coordinates' in feature['geometry']:
            coords = feature['geometry']['coordinates']
            if feature['geometry']['type'] == 'Point':
                print(f"  Location: {coords[1]:.4f}, {coords[0]:.4f}")
            elif feature['geometry']['type'] == 'Polygon':
                # Get centroid approximation
                if coords and len(coords[0]) > 0:
                    lons = [p[0] for p in coords[0]]
                    lats = [p[1] for p in coords[0]]
                    center_lon = sum(lons) / len(lons)
                    center_lat = sum(lats) / len(lats)
                    print(f"  Center: {center_lat:.4f}, {center_lon:.4f}")
        print()
    
    # Save results
    output_file = output_dir / 'mining_features.geojson'
    extractor.save_mining_features(results, output_file)
    
    print(f"\nAll mining features have been saved to: {output_file}")
    print("You can now load this file into QGIS or other GIS software to visualize mine locations.")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())