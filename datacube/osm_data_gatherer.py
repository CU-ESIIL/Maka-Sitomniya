#!/usr/bin/env python
"""
OSM Data Gatherer for Black Hills Region

This script gathers OpenStreetMap data for the Black Hills region using the
bounding box coordinates defined in config.py. It supports downloading various
types of OSM data using the Overpass API.
"""

import os
import sys
import json
import time
import logging
from typing import Dict, List, Optional, Union
from pathlib import Path
import requests
from datetime import datetime

# Import configuration
from config import BLACK_HILLS_BBOX_WGS84, BLACK_HILLS_BBOX_STRING, DATA_DIR

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class OSMDataGatherer:
    """Class to handle OSM data collection for the Black Hills region."""
    
    def __init__(self, output_dir: Optional[str] = None):
        """
        Initialize the OSM data gatherer.
        
        Args:
            output_dir: Directory to save downloaded data. Defaults to DATA_DIR/osm
        """
        self.bbox = BLACK_HILLS_BBOX_WGS84
        self.bbox_string = BLACK_HILLS_BBOX_STRING
        self.output_dir = Path(output_dir) if output_dir else Path(DATA_DIR) / "osm"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Overpass API endpoint
        self.overpass_url = "https://overpass-api.de/api/interpreter"
        
        # Create subdirectories for different data types
        self.roads_dir = self.output_dir / "roads"
        self.buildings_dir = self.output_dir / "buildings"
        self.landuse_dir = self.output_dir / "landuse"
        self.natural_dir = self.output_dir / "natural"
        self.amenities_dir = self.output_dir / "amenities"
        self.boundaries_dir = self.output_dir / "boundaries"
        self.raw_dir = self.output_dir / "raw"
        
        for dir_path in [self.roads_dir, self.buildings_dir, self.landuse_dir, 
                        self.natural_dir, self.amenities_dir, self.boundaries_dir, self.raw_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)
    
    def _build_overpass_query(self, query_type: str, elements: List[str]) -> str:
        """
        Build an Overpass API query for the Black Hills bounding box.
        
        Args:
            query_type: Type of OSM element ('way', 'node', 'relation')
            elements: List of key=value pairs to search for
            
        Returns:
            Formatted Overpass query string
        """
        # Bounding box format: south, west, north, east
        bbox = f"{self.bbox['south']},{self.bbox['west']},{self.bbox['north']},{self.bbox['east']}"
        
        query_parts = []
        for element in elements:
            query_parts.append(f'{query_type}[{element}]({bbox});')
        
        query = f"""
        [out:json][timeout:300];
        (
        {chr(10).join(query_parts)}
        );
        out geom;
        """
        return query
    
    def _execute_overpass_query(self, query: str, max_retries: int = 3) -> Optional[Dict]:
        """
        Execute an Overpass API query with retry logic.
        
        Args:
            query: Overpass query string
            max_retries: Maximum number of retry attempts
            
        Returns:
            JSON response from Overpass API or None if failed
        """
        for attempt in range(max_retries):
            try:
                logger.info(f"Executing Overpass query (attempt {attempt + 1}/{max_retries})")
                response = requests.post(
                    self.overpass_url,
                    data=query,
                    timeout=600,  # 10 minute timeout
                    headers={'User-Agent': 'OSM_BlackHills_DataGatherer/1.0'}
                )
                response.raise_for_status()
                
                return response.json()
                
            except requests.exceptions.RequestException as e:
                logger.warning(f"Request failed on attempt {attempt + 1}: {e}")
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt  # Exponential backoff
                    logger.info(f"Waiting {wait_time} seconds before retry...")
                    time.sleep(wait_time)
                else:
                    logger.error(f"All {max_retries} attempts failed")
                    return None
    
    def _save_data(self, data: Dict, filename: str, subdir: Path) -> str:
        """
        Save data to a JSON file with timestamp.
        
        Args:
            data: Data to save
            filename: Base filename
            subdir: Subdirectory to save in
            
        Returns:
            Full path to saved file
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        full_filename = f"{filename}_{timestamp}.json"
        file_path = subdir / full_filename
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Saved {len(data.get('elements', []))} elements to {file_path}")
        return str(file_path)
    
    def gather_roads(self) -> Optional[str]:
        """Gather road network data."""
        logger.info("Gathering road network data...")
        
        road_types = [
            'highway=motorway',
            'highway=trunk',
            'highway=primary',
            'highway=secondary',
            'highway=tertiary',
            'highway=residential',
            'highway=service',
            'highway=track',
            'highway=path',
            'highway=footway',
            'highway=cycleway'
        ]
        
        query = self._build_overpass_query('way', road_types)
        data = self._execute_overpass_query(query)
        
        if data:
            return self._save_data(data, "roads", self.roads_dir)
        return None
    
    def gather_buildings(self) -> Optional[str]:
        """Gather building data."""
        logger.info("Gathering building data...")
        
        building_queries = [
            'building',
            'building=yes',
            'building=house',
            'building=commercial',
            'building=industrial',
            'building=school',
            'building=hospital',
            'building=church'
        ]
        
        query = self._build_overpass_query('way', building_queries)
        data = self._execute_overpass_query(query)
        
        if data:
            return self._save_data(data, "buildings", self.buildings_dir)
        return None
    
    def gather_landuse(self) -> Optional[str]:
        """Gather land use data."""
        logger.info("Gathering land use data...")
        
        landuse_types = [
            'landuse=forest',
            'landuse=farmland',
            'landuse=residential',
            'landuse=commercial',
            'landuse=industrial',
            'landuse=recreation_ground',
            'landuse=cemetery',
            'landuse=meadow',
            'landuse=grass'
        ]
        
        query = self._build_overpass_query('way', landuse_types)
        data = self._execute_overpass_query(query)
        
        if data:
            return self._save_data(data, "landuse", self.landuse_dir)
        return None
    
    def gather_natural_features(self) -> Optional[str]:
        """Gather natural features data."""
        logger.info("Gathering natural features data...")
        
        natural_features = [
            'natural=water',
            'natural=wood',
            'natural=grassland',
            'natural=scrub',
            'natural=bare_rock',
            'natural=peak',
            'natural=valley',
            'natural=ridge',
            'waterway=river',
            'waterway=stream',
            'waterway=creek'
        ]
        
        # Include both ways and nodes for natural features
        way_query = self._build_overpass_query('way', natural_features)
        node_query = self._build_overpass_query('node', natural_features)
        
        # Combine queries
        bbox = f"{self.bbox['south']},{self.bbox['west']},{self.bbox['north']},{self.bbox['east']}"
        combined_query = f"""
        [out:json][timeout:300];
        (
        {chr(10).join([f'way[{feat}]({bbox});' for feat in natural_features])}
        {chr(10).join([f'node[{feat}]({bbox});' for feat in natural_features])}
        );
        out geom;
        """
        
        data = self._execute_overpass_query(combined_query)
        
        if data:
            return self._save_data(data, "natural_features", self.natural_dir)
        return None
    
    def gather_amenities(self) -> Optional[str]:
        """Gather amenities and points of interest."""
        logger.info("Gathering amenities and POIs...")
        
        amenities = [
            'amenity=restaurant',
            'amenity=fuel',
            'amenity=hospital',
            'amenity=school',
            'amenity=bank',
            'amenity=post_office',
            'amenity=parking',
            'amenity=toilets',
            'tourism=hotel',
            'tourism=motel',
            'tourism=campsite',
            'tourism=picnic_site',
            'tourism=viewpoint',
            'tourism=information',
            'shop'
        ]
        
        # Include both ways and nodes for amenities
        bbox = f"{self.bbox['south']},{self.bbox['west']},{self.bbox['north']},{self.bbox['east']}"
        combined_query = f"""
        [out:json][timeout:300];
        (
        {chr(10).join([f'way[{amenity}]({bbox});' for amenity in amenities])}
        {chr(10).join([f'node[{amenity}]({bbox});' for amenity in amenities])}
        );
        out geom;
        """
        
        data = self._execute_overpass_query(combined_query)
        
        if data:
            return self._save_data(data, "amenities", self.amenities_dir)
        return None
    
    def gather_boundaries(self) -> Optional[str]:
        """Gather administrative boundaries."""
        logger.info("Gathering administrative boundaries...")
        
        boundary_types = [
            'boundary=administrative',
            'boundary=national_park',
            'boundary=protected_area',
            'boundary=city',
            'boundary=county'
        ]
        
        query = self._build_overpass_query('relation', boundary_types)
        data = self._execute_overpass_query(query)
        
        if data:
            return self._save_data(data, "boundaries", self.boundaries_dir)
        return None
    
    def gather_all_data(self) -> Dict[str, Optional[str]]:
        """
        Gather all types of OSM data for the Black Hills region.
        
        Returns:
            Dictionary mapping data type to file path (or None if failed)
        """
        logger.info(f"Starting OSM data collection for Black Hills region")
        logger.info(f"Bounding box: {self.bbox}")
        logger.info(f"Output directory: {self.output_dir}")
        
        results = {}
        
        # Gather each type of data
        data_types = [
            ('roads', self.gather_roads),
            ('buildings', self.gather_buildings),
            ('landuse', self.gather_landuse),
            ('natural_features', self.gather_natural_features),
            ('amenities', self.gather_amenities),
            ('boundaries', self.gather_boundaries)
        ]
        
        for data_type, gather_func in data_types:
            try:
                result = gather_func()
                results[data_type] = result
                
                # Add delay between requests to be respectful to the API
                time.sleep(2)
                
            except Exception as e:
                logger.error(f"Error gathering {data_type}: {e}")
                results[data_type] = None
        
        # Save summary
        summary = {
            'collection_date': datetime.now().isoformat(),
            'bbox': self.bbox,
            'results': results,
            'total_files': len([r for r in results.values() if r is not None])
        }
        
        summary_path = self.output_dir / f"collection_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(summary_path, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Collection complete. Summary saved to {summary_path}")
        logger.info(f"Successfully gathered {summary['total_files']} out of {len(data_types)} data types")
        
        return results


def main():
    """Main function to run the OSM data gatherer."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Gather OSM data for the Black Hills region')
    parser.add_argument('--output-dir', type=str, help='Output directory for downloaded data')
    parser.add_argument('--data-type', type=str, choices=['roads', 'buildings', 'landuse', 'natural', 'amenities', 'boundaries', 'all'], 
                       default='all', help='Type of data to gather')
    
    args = parser.parse_args()
    
    # Create gatherer instance
    gatherer = OSMDataGatherer(output_dir=args.output_dir)
    
    # Gather specified data type
    if args.data_type == 'all':
        results = gatherer.gather_all_data()
    else:
        method_map = {
            'roads': gatherer.gather_roads,
            'buildings': gatherer.gather_buildings,
            'landuse': gatherer.gather_landuse,
            'natural': gatherer.gather_natural_features,
            'amenities': gatherer.gather_amenities,
            'boundaries': gatherer.gather_boundaries
        }
        
        if args.data_type in method_map:
            result = method_map[args.data_type]()
            results = {args.data_type: result}
        else:
            logger.error(f"Unknown data type: {args.data_type}")
            return 1
    
    # Print results
    successful = len([r for r in results.values() if r is not None])
    total = len(results)
    
    print(f"\nOSM Data Collection Complete!")
    print(f"Successfully gathered {successful}/{total} data types")
    print(f"Data saved to: {gatherer.output_dir}")
    
    if successful < total:
        print(f"\nFailed to gather:")
        for data_type, result in results.items():
            if result is None:
                print(f"  - {data_type}")
    
    return 0 if successful > 0 else 1


if __name__ == "__main__":
    sys.exit(main())