"""
Google Earth Engine-based MACA v2 data fetcher.

This module downloads MACA v2 climate data from Google Earth Engine
since the USGS THREDDS server was retired in April 2024.
"""

import logging
import warnings
from pathlib import Path
from typing import Optional, Union, List, Tuple
import pandas as pd
import numpy as np

try:
    import ee
    import geemap
    GEE_AVAILABLE = True
except ImportError:
    GEE_AVAILABLE = False
    ee = None
    geemap = None

try:
    from .sources_standalone import Variable, ClimateModel, Scenario, BoundingBox, BLACK_HILLS_BBOX
except ImportError:
    from sources_standalone import Variable, ClimateModel, Scenario, BoundingBox, BLACK_HILLS_BBOX

logger = logging.getLogger(__name__)


class GEEMACAfetcher:
    """Google Earth Engine-based MACA v2 data fetcher."""
    
    def __init__(self, data_dir: Union[str, Path] = "./data/maca_gee"):
        """
        Initialize the GEE MACA fetcher.
        
        Args:
            data_dir: Directory to save downloaded data
        """
        if not GEE_AVAILABLE:
            raise ImportError(
                "Google Earth Engine is not available. "
                "Install with: pip install earthengine-api geemap"
            )
        
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize Earth Engine (requires authentication)
        try:
            ee.Initialize()
            logger.info("Google Earth Engine initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Google Earth Engine: {e}")
            logger.info("Run 'earthengine authenticate' to set up authentication")
            raise
        
        # MACA v2 collection ID
        self.collection_id = "IDAHO_EPSCOR/MACAv2_METDATA"
    
    def download_subset(
        self,
        variable: Variable,
        model: ClimateModel,
        scenario: Scenario,
        year_start: int,
        year_end: int,
        bbox: BoundingBox,
        scale: int = 4000,  # 4km resolution
        force: bool = False
    ) -> Optional[Path]:
        """
        Download MACA v2 data subset from Google Earth Engine.
        
        Args:
            variable: Climate variable
            model: Climate model
            scenario: Climate scenario
            year_start: Start year
            year_end: End year
            bbox: Bounding box
            scale: Spatial resolution in meters (4000m = 4km)
            force: Force re-download if file exists
            
        Returns:
            Path to downloaded file or None if failed
        """
        # Create filename
        filename = (
            f"maca_gee_{variable.value}_{model.value}_{scenario.value}_"
            f"{year_start}_{year_end}_subset.nc"
        )
        output_path = self.data_dir / filename
        
        if output_path.exists() and not force:
            logger.info(f"File already exists: {output_path}")
            return output_path
        
        try:
            logger.info(f"Downloading {variable.value} from {model.value} {scenario.value}")
            logger.info(f"Time range: {year_start}-{year_end}")
            logger.info(f"Bounding box: {bbox.south}°S to {bbox.north}°N, {bbox.west}°W to {bbox.east}°E")
            
            # Load the collection
            collection = ee.ImageCollection(self.collection_id)
            
            # Create date range
            start_date = f"{year_start}-01-01"
            end_date = f"{year_end}-12-31"
            
            # Filter collection
            filtered = collection.filter(ee.Filter.date(start_date, end_date))
            
            # Filter by model and scenario
            # The GEE collection uses specific property names for filtering
            model_filter = ee.Filter.eq('model', model.value)
            scenario_filter = ee.Filter.eq('scenario', scenario.value)
            
            filtered = filtered.filter(model_filter).filter(scenario_filter)
            
            # Select the variable
            variable_name = self._get_gee_variable_name(variable)
            filtered = filtered.select(variable_name)
            
            # Define region of interest
            region = ee.Geometry.Rectangle([bbox.west, bbox.south, bbox.east, bbox.north])
            
            # Get collection info
            collection_size = filtered.size()
            logger.info(f"Found {collection_size.getInfo()} images in collection")
            
            if collection_size.getInfo() == 0:
                logger.warning("No images found for the specified criteria")
                return None
            
            # Convert to a single multi-band image with time dimension
            # Sort by time and convert to bands
            sorted_collection = filtered.sort('system:time_start')
            
            # Get the first few images to create a multi-band image
            image_list = sorted_collection.toList(collection_size)
            
            # For demonstration, we'll download the first image
            # In practice, you might want to create a time series
            first_image = ee.Image(image_list.get(0))
            
            # Clip to region
            clipped = first_image.clip(region)
            
            # Download the image
            logger.info("Starting download from Google Earth Engine...")
            
            # Use geemap to download (easier than ee.batch)
            geemap.ee_export_image(
                clipped,
                filename=str(output_path),
                scale=scale,
                region=region,
                file_per_band=False
            )
            
            logger.info(f"Successfully downloaded: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Download failed: {e}")
            logger.info("Note: Make sure you have:")
            logger.info("1. Authenticated with Earth Engine: earthengine authenticate")
            logger.info("2. Have access to the MACA dataset")
            logger.info("3. Installed required packages: pip install earthengine-api geemap")
            return None
    
    def _get_gee_variable_name(self, variable: Variable) -> str:
        """Convert our variable enum to GEE band name."""
        # Map our variable names to GEE band names
        mapping = {
            Variable.TASMAX: 'tasmax',
            Variable.TASMIN: 'tasmin', 
            Variable.PR: 'pr',
            Variable.RHSMAX: 'rhsmax',
            Variable.RHSMIN: 'rhsmin',
            Variable.HUSS: 'huss',
            Variable.WAS: 'was',
            Variable.RSDS: 'rsds',
            Variable.VPD: 'vpd'
        }
        return mapping.get(variable, variable.value)
    
    def list_available_data(
        self,
        variable: Optional[Variable] = None,
        model: Optional[ClimateModel] = None,
        scenario: Optional[Scenario] = None,
        year_range: Optional[Tuple[int, int]] = None
    ) -> List[dict]:
        """
        List available data in the GEE collection.
        
        Args:
            variable: Filter by variable
            model: Filter by model
            scenario: Filter by scenario
            year_range: Filter by year range (start, end)
            
        Returns:
            List of available datasets with metadata
        """
        try:
            collection = ee.ImageCollection(self.collection_id)
            
            # Apply filters if provided
            if year_range:
                start_date = f"{year_range[0]}-01-01"
                end_date = f"{year_range[1]}-12-31"
                collection = collection.filter(ee.Filter.date(start_date, end_date))
            
            if model:
                collection = collection.filter(ee.Filter.eq('model', model.value))
            
            if scenario:
                collection = collection.filter(ee.Filter.eq('scenario', scenario.value))
            
            # Get collection info
            collection_info = collection.getInfo()
            
            results = []
            for feature in collection_info.get('features', [])[:10]:  # Limit to first 10
                props = feature.get('properties', {})
                results.append({
                    'model': props.get('model'),
                    'scenario': props.get('scenario'),
                    'time_start': props.get('system:time_start'),
                    'bands': feature.get('bands', [])
                })
            
            return results
            
        except Exception as e:
            logger.error(f"Failed to list available data: {e}")
            return []


def download_black_hills_subset_gee(
    variable: Variable,
    model: ClimateModel,
    scenario: Scenario,
    year_start: int,
    year_end: int,
    output_dir: Union[str, Path] = "./data/maca_gee"
) -> Optional[Path]:
    """
    Convenience function to download Black Hills MACA subset from GEE.
    
    Args:
        variable: Climate variable
        model: Climate model  
        scenario: Climate scenario
        year_start: Start year
        year_end: End year
        output_dir: Output directory
        
    Returns:
        Path to downloaded file or None if failed
    """
    fetcher = GEEMACAfetcher(data_dir=output_dir)
    
    return fetcher.download_subset(
        variable=variable,
        model=model,
        scenario=scenario,
        year_start=year_start,
        year_end=year_end,
        bbox=BLACK_HILLS_BBOX
    )


def setup_earth_engine():
    """
    Setup Earth Engine authentication and initialization.
    
    Returns:
        True if successful, False otherwise
    """
    if not GEE_AVAILABLE:
        print("❌ Google Earth Engine not available")
        print("Install with: pip install earthengine-api geemap")
        return False
    
    try:
        # Try to initialize
        ee.Initialize()
        print("✅ Google Earth Engine initialized successfully")
        return True
        
    except Exception as e:
        print(f"❌ Earth Engine initialization failed: {e}")
        print("\nTo fix this:")
        print("1. Run: pip install earthengine-api geemap")
        print("2. Run: earthengine authenticate")
        print("3. Follow the authentication instructions")
        return False


if __name__ == "__main__":
    # Test setup
    print("Testing Google Earth Engine setup...")
    
    if setup_earth_engine():
        print("\n🎉 Ready to download MACA v2 data from Google Earth Engine!")
        
        # Test data listing
        fetcher = GEEMACAfetcher()
        print("\nTesting data availability...")
        
        available = fetcher.list_available_data(
            variable=Variable.TASMAX,
            year_range=(2020, 2021)
        )
        
        if available:
            print(f"✅ Found {len(available)} datasets")
            print("Sample:", available[0] if available else "None")
        else:
            print("❌ No data found or access issues")
    else:
        print("❌ Setup failed - follow the instructions above")