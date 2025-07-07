#!/usr/bin/env python
"""
OSM to GeoJSON Converter

Converts OSM JSON data downloaded by osm_data_gatherer.py to GeoJSON format.
Handles ways, nodes, and relations from Overpass API output.
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
import argparse
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class OSMToGeoJSONConverter:
    """Convert OSM JSON data to GeoJSON format."""
    
    def __init__(self):
        """Initialize the converter."""
        pass
    
    def _convert_node_to_geojson(self, node: Dict) -> Dict:
        """
        Convert an OSM node to a GeoJSON Point feature.
        
        Args:
            node: OSM node dictionary
            
        Returns:
            GeoJSON Point feature
        """
        properties = {
            'osm_id': node['id'],
            'osm_type': 'node'
        }
        
        # Add tags as properties
        if 'tags' in node:
            properties.update(node['tags'])
        
        return {
            'type': 'Feature',
            'geometry': {
                'type': 'Point',
                'coordinates': [node['lon'], node['lat']]
            },
            'properties': properties
        }
    
    def _convert_way_to_geojson(self, way: Dict) -> Optional[Dict]:
        """
        Convert an OSM way to a GeoJSON LineString or Polygon feature.
        
        Args:
            way: OSM way dictionary
            
        Returns:
            GeoJSON LineString or Polygon feature, or None if invalid
        """
        if 'geometry' not in way or not way['geometry']:
            logger.warning(f"Way {way['id']} has no geometry, skipping")
            return None
        
        coordinates = [[point['lon'], point['lat']] for point in way['geometry']]
        
        if len(coordinates) < 2:
            logger.warning(f"Way {way['id']} has insufficient coordinates, skipping")
            return None
        
        properties = {
            'osm_id': way['id'],
            'osm_type': 'way'
        }
        
        # Add tags as properties
        if 'tags' in way:
            properties.update(way['tags'])
        
        # Determine if this should be a Polygon or LineString
        # If first and last coordinates are the same, it's a closed way (potential polygon)
        is_closed = (coordinates[0] == coordinates[-1])
        
        # Check if this is likely a polygon based on tags
        polygon_tags = {
            'building', 'landuse', 'natural', 'leisure', 'amenity', 
            'shop', 'office', 'industrial', 'residential', 'commercial',
            'area'
        }
        
        is_area = False
        if 'tags' in way:
            # Check if any tag suggests this is an area
            is_area = any(tag in way['tags'] for tag in polygon_tags)
            # Also check explicit area tag
            if 'area' in way['tags']:
                is_area = way['tags']['area'].lower() in ['yes', 'true', '1']
        
        if is_closed and is_area:
            # Create a Polygon
            geometry = {
                'type': 'Polygon',
                'coordinates': [coordinates]
            }
        else:
            # Create a LineString
            geometry = {
                'type': 'LineString',
                'coordinates': coordinates
            }
        
        return {
            'type': 'Feature',
            'geometry': geometry,
            'properties': properties
        }
    
    def _convert_relation_to_geojson(self, relation: Dict) -> Optional[Dict]:
        """
        Convert an OSM relation to a GeoJSON feature.
        
        Args:
            relation: OSM relation dictionary
            
        Returns:
            GeoJSON feature or None if cannot be converted
        """
        properties = {
            'osm_id': relation['id'],
            'osm_type': 'relation'
        }
        
        # Add tags as properties
        if 'tags' in relation:
            properties.update(relation['tags'])
        
        # For now, create a simple representation
        # More complex relation handling could be added later
        if 'bounds' in relation:
            bounds = relation['bounds']
            coordinates = [[
                [bounds['minlon'], bounds['minlat']],
                [bounds['maxlon'], bounds['minlat']],
                [bounds['maxlon'], bounds['maxlat']],
                [bounds['minlon'], bounds['maxlat']],
                [bounds['minlon'], bounds['minlat']]
            ]]
            
            return {
                'type': 'Feature',
                'geometry': {
                    'type': 'Polygon',
                    'coordinates': coordinates
                },
                'properties': properties
            }
        
        logger.warning(f"Relation {relation['id']} has no bounds, skipping")
        return None
    
    def convert_osm_to_geojson(self, osm_data: Dict) -> Dict:
        """
        Convert OSM JSON data to GeoJSON format.
        
        Args:
            osm_data: OSM data dictionary from Overpass API
            
        Returns:
            GeoJSON FeatureCollection
        """
        features = []
        
        if 'elements' not in osm_data:
            logger.warning("No elements found in OSM data")
            return {
                'type': 'FeatureCollection',
                'features': []
            }
        
        for element in osm_data['elements']:
            feature = None
            
            if element['type'] == 'node':
                feature = self._convert_node_to_geojson(element)
            elif element['type'] == 'way':
                feature = self._convert_way_to_geojson(element)
            elif element['type'] == 'relation':
                feature = self._convert_relation_to_geojson(element)
            else:
                logger.warning(f"Unknown element type: {element['type']}")
                continue
            
            if feature:
                features.append(feature)
        
        # Create GeoJSON FeatureCollection
        geojson = {
            'type': 'FeatureCollection',
            'features': features
        }
        
        # Add metadata if available
        if 'osm3s' in osm_data:
            geojson['metadata'] = {
                'generator': osm_data.get('generator', 'Unknown'),
                'timestamp': osm_data['osm3s'].get('timestamp_osm_base', ''),
                'copyright': osm_data['osm3s'].get('copyright', ''),
                'feature_count': len(features)
            }
        
        return geojson
    
    def convert_file(self, input_file: str, output_file: Optional[str] = None) -> str:
        """
        Convert a single OSM JSON file to GeoJSON.
        
        Args:
            input_file: Path to input OSM JSON file
            output_file: Path to output GeoJSON file (optional)
            
        Returns:
            Path to output file
        """
        input_path = Path(input_file)
        
        if not input_path.exists():
            raise FileNotFoundError(f"Input file not found: {input_file}")
        
        # Generate output filename if not provided
        if output_file is None:
            output_file = input_path.with_suffix('.geojson')
        
        output_path = Path(output_file)
        
        # Load OSM data
        logger.info(f"Loading OSM data from {input_path}")
        with open(input_path, 'r', encoding='utf-8') as f:
            osm_data = json.load(f)
        
        # Convert to GeoJSON
        logger.info(f"Converting to GeoJSON...")
        geojson = self.convert_osm_to_geojson(osm_data)
        
        # Save GeoJSON
        logger.info(f"Saving GeoJSON to {output_path}")
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(geojson, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Converted {len(geojson['features'])} features")
        return str(output_path)
    
    def convert_directory(self, input_dir: str, output_dir: Optional[str] = None) -> Dict[str, str]:
        """
        Convert all OSM JSON files in a directory to GeoJSON.
        
        Args:
            input_dir: Directory containing OSM JSON files
            output_dir: Output directory (optional, defaults to input_dir/geojson)
            
        Returns:
            Dictionary mapping input files to output files
        """
        input_path = Path(input_dir)
        
        if not input_path.exists():
            raise FileNotFoundError(f"Input directory not found: {input_dir}")
        
        # Set output directory
        if output_dir is None:
            output_path = input_path / 'geojson'
        else:
            output_path = Path(output_dir)
        
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Find all JSON files
        json_files = list(input_path.rglob('*.json'))
        
        if not json_files:
            logger.warning(f"No JSON files found in {input_dir}")
            return {}
        
        results = {}
        
        for json_file in json_files:
            # Skip collection summary files
            if 'collection_summary' in json_file.name:
                continue
            
            try:
                # Maintain directory structure
                relative_path = json_file.relative_to(input_path)
                output_file = output_path / relative_path.with_suffix('.geojson')
                
                # Create output subdirectory if needed
                output_file.parent.mkdir(parents=True, exist_ok=True)
                
                # Convert file
                result = self.convert_file(str(json_file), str(output_file))
                results[str(json_file)] = result
                
            except Exception as e:
                logger.error(f"Error converting {json_file}: {e}")
                results[str(json_file)] = None
        
        logger.info(f"Converted {len([r for r in results.values() if r])} out of {len(results)} files")
        return results


def main():
    """Main function to run the OSM to GeoJSON converter."""
    parser = argparse.ArgumentParser(description='Convert OSM JSON data to GeoJSON format')
    parser.add_argument('input', help='Input OSM JSON file or directory')
    parser.add_argument('--output', '-o', help='Output GeoJSON file or directory')
    parser.add_argument('--directory', '-d', action='store_true', 
                       help='Process entire directory instead of single file')
    
    args = parser.parse_args()
    
    converter = OSMToGeoJSONConverter()
    
    try:
        if args.directory:
            results = converter.convert_directory(args.input, args.output)
            
            # Print results
            successful = len([r for r in results.values() if r is not None])
            total = len(results)
            
            print(f"\nConversion Complete!")
            print(f"Successfully converted {successful}/{total} files")
            
            if successful < total:
                print(f"\nFailed conversions:")
                for input_file, output_file in results.items():
                    if output_file is None:
                        print(f"  - {input_file}")
        else:
            output_file = converter.convert_file(args.input, args.output)
            print(f"Successfully converted {args.input} to {output_file}")
            
    except Exception as e:
        logger.error(f"Conversion failed: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())