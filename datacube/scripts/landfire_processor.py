#!/usr/bin/env python
"""
LANDFIRE Vegetation Data Processor

This module provides functionality to download and process LANDFIRE Existing Vegetation 
Type (EVT) data, allowing for integration into the datacube framework with spatial
and temporal bucketing capabilities.

The LandfireProcessor class can:
1. Download LANDFIRE EVT data for specified bounding boxes
2. Extract and process the data into xarray Datasets
3. Reproject and resample the data to match other datasets
4. Apply spatial bucketing for integration with the datacube
5. Save processed datasets to NetCDF files

Usage:
    processor = LandfireProcessor(bbox="-107.71 46.57 -106.03 47.35")
    
    # Download EVT data (220 = 2020 version)
    processor.download_data("220EVT")
    
    # Process into xarray Dataset
    dataset = processor.create_dataset()
    
    # Apply spatial bucketing
    bucketed = processor.bucket_spatial(
        lat_bucket_size=0.01,
        lon_bucket_size=0.01,
        agg_method="mode"  # Use most common value for categorical data
    )
    
    # Save the processed dataset
    processor.save_dataset(bucketed, "landfire_evt_processed.nc")
"""

import os
import tempfile
import zipfile
import numpy as np
import xarray as xr
import rasterio
from rasterio.transform import from_origin
import landfire
from enum import Enum
from typing import Optional, Union, List, Tuple, Dict

class AggregationMethod(Enum):
    """
    Enumeration of supported aggregation methods for categorical data.
    
    Available methods:
    - MODE: Most common value (most appropriate for categorical data like EVT)
    - MAJORITY: Synonym for MODE
    - FIRST: First value encountered
    - LAST: Last value encountered
    """
    MODE = "mode"
    MAJORITY = "majority"
    FIRST = "first"
    LAST = "last"

class LandfireProcessor:
    """
    Processor for LANDFIRE vegetation data.
    
    This class handles downloading, processing, and bucketing LANDFIRE
    data (primarily Existing Vegetation Type) for integration into datacubes.
    """
    
    def __init__(self, bbox: str, data_dir: Optional[str] = None):
        """
        Initialize the LANDFIRE processor.
        
        Args:
            bbox: Bounding box in format "minx miny maxx maxy" (longitude/latitude)
            data_dir: Directory to store downloaded data (uses temp dir if None)
        """
        self.bbox = bbox
        
        # Parse the bounding box into components
        self._parse_bbox()
        
        # Set up data directory
        if data_dir:
            self.data_dir = data_dir
            os.makedirs(data_dir, exist_ok=True)
        else:
            # Create a temporary directory that will persist during object lifetime
            self._temp_dir = tempfile.TemporaryDirectory()
            self.data_dir = self._temp_dir.name
        
        # Initialize landfire client and dataset containers
        self.lf_client = landfire.Landfire(bbox=bbox)
        self.raw_data_path = None
        self.raw_dataset = None
        self.processed_dataset = None
        
        print(f"Initialized LANDFIRE processor with bbox: {bbox}")
        print(f"Data will be stored in: {self.data_dir}")
    
    def _parse_bbox(self):
        """Parse the bounding box string into component values."""
        parts = self.bbox.split()
        if len(parts) != 4:
            raise ValueError("Bounding box must be in format 'minx miny maxx maxy'")
        
        self.minx = float(parts[0])
        self.miny = float(parts[1])
        self.maxx = float(parts[2])
        self.maxy = float(parts[3])
    
    def download_data(self, layer: str) -> str:
        """
        Download LANDFIRE data for the specified layer.
        
        Args:
            layer: LANDFIRE layer ID (e.g., "220EVT" for 2020 Existing Vegetation Type)
        
        Returns:
            Path to the downloaded data file
        """
        # Create the output path for the zip file
        output_path = os.path.join(self.data_dir, f"landfire_{layer}.zip")
        
        print(f"Downloading LANDFIRE {layer} data...")
        
        # Request the data for the specified layer
        self.lf_client.request_data(
            layers=[layer],
            output_path=output_path
        )
        
        self.raw_data_path = output_path
        print(f"Data downloaded to: {output_path}")
        
        return output_path
    
    def extract_data(self, output_dir: Optional[str] = None) -> str:
        """
        Extract the downloaded ZIP file.
        
        Args:
            output_dir: Directory to extract files to (uses data_dir if None)
            
        Returns:
            Path to the directory containing extracted files
        """
        if not self.raw_data_path:
            raise ValueError("No data has been downloaded yet. Call download_data first.")
        
        if output_dir is None:
            output_dir = os.path.join(self.data_dir, "extracted")
            os.makedirs(output_dir, exist_ok=True)
        
        print(f"Extracting data to: {output_dir}")
        
        with zipfile.ZipFile(self.raw_data_path, 'r') as zip_ref:
            zip_ref.extractall(output_dir)
        
        # Find the extracted TIFF file
        tiff_files = [f for f in os.listdir(output_dir) if f.endswith('.tif')]
        
        if not tiff_files:
            raise FileNotFoundError("No TIFF files found in extracted data")
        
        self.tiff_path = os.path.join(output_dir, tiff_files[0])
        print(f"Found TIFF file: {self.tiff_path}")
        
        return output_dir
    
    def create_dataset(self) -> xr.Dataset:
        """
        Create an xarray Dataset from the extracted TIFF file.
        
        Returns:
            xarray Dataset containing the LANDFIRE data
        """
        if not hasattr(self, 'tiff_path'):
            # Extract if not already done
            self.extract_data()
        
        print(f"Creating xarray dataset from: {self.tiff_path}")
        
        # Open the TIFF file with rasterio
        with rasterio.open(self.tiff_path) as src:
            # Read the data
            data = src.read(1)  # Read the first band
            
            # Get the metadata
            transform = src.transform
            crs = src.crs
            
            # Create coordinates from transform
            height, width = data.shape
            rows = np.arange(height)
            cols = np.arange(width)
            
            # Get the coordinates in the original CRS
            x_coords = transform.c + cols * transform.a
            y_coords = transform.f + rows * transform.e
            
            # Get nodata value
            nodata = src.nodata
            
            # Create lat/lon coordinates using the CRS
            # This is a simplification - proper reprojection would be better
            # For EPSG:4326 (WGS84), x is longitude and y is latitude
            # However this depends on the source CRS and may need to be adapted
            
            # Create DataArray
            da = xr.DataArray(
                data=data,
                dims=["y", "x"],
                coords={
                    "y": y_coords,
                    "x": x_coords
                },
                attrs={
                    "crs": str(crs),
                    "transform": str(transform),
                    "nodata": nodata
                }
            )
            
            # Create Dataset
            ds = xr.Dataset(
                data_vars={"evt": da},
                attrs={
                    "crs": str(crs),
                    "transform": str(transform)
                }
            )
            
            self.raw_dataset = ds
            print("xarray dataset created successfully")
            
            return ds
    
    def reproject_to_latlon(self) -> xr.Dataset:
        """
        Reproject the dataset to latitude/longitude coordinates (EPSG:4326).
        
        This is important for integration with other datacube datasets.
        
        Returns:
            Reprojected xarray Dataset
        """
        if self.raw_dataset is None:
            self.create_dataset()
        
        print("Reprojecting dataset to lat/lon coordinates...")
        
        # Try to use rioxarray for proper reprojection if available
        try:
            import rioxarray
            # Convert to rioxarray
            rio_ds = self.raw_dataset.rio.write_crs(self.raw_dataset.attrs['crs'])
            # Reproject to WGS84
            reprojected = rio_ds.rio.reproject("EPSG:4326")
            print("Used rioxarray for proper reprojection")
        except (ImportError, Exception) as e:
            print(f"Warning: Could not use rioxarray for reprojection: {e}")
            print("Falling back to simplified projection (not accurate)")
            
            # Simple fallback approximation
            height, width = self.raw_dataset.evt.shape
            
            # Create evenly spaced lat/lon coordinates within the bounding box
            lats = np.linspace(self.miny, self.maxy, height)
            lons = np.linspace(self.minx, self.maxx, width)
            
            # Create a simplified reprojection
            reprojected = xr.Dataset(
                data_vars={
                    "evt": (["lat", "lon"], self.raw_dataset.evt.values)
                },
                coords={
                    "lat": lats,
                    "lon": lons
                },
                attrs=dict(self.raw_dataset.attrs, crs="EPSG:4326")
            )
        
        self.processed_dataset = reprojected
        print("Reprojection completed")
        
        return reprojected
    
    def bucket_spatial(self, 
                      lat_bucket_size: float, 
                      lon_bucket_size: float,
                      agg_method: Union[AggregationMethod, str] = AggregationMethod.MODE) -> xr.Dataset:
        """
        Bucket the data into specified spatial resolution.
        
        Args:
            lat_bucket_size: Size of latitude buckets in degrees
            lon_bucket_size: Size of longitude buckets in degrees
            agg_method: Method to aggregate data within buckets
            
        Returns:
            Dataset with bucketed spatial dimensions
        """
        if self.processed_dataset is None:
            self.reproject_to_latlon()
        
        dataset = self.processed_dataset
        
        # Convert string method to enum if needed
        if isinstance(agg_method, str):
            try:
                agg_method = AggregationMethod(agg_method.lower())
            except ValueError:
                raise ValueError(f"Unsupported aggregation method: {agg_method}")
        
        # Identify lat/lon dimensions
        lat_dim = "lat"
        lon_dim = "lon"
        
        # Calculate new grid
        lat_bins = np.arange(
            float(dataset[lat_dim].min()), 
            float(dataset[lat_dim].max()) + lat_bucket_size, 
            lat_bucket_size
        )
        lon_bins = np.arange(
            float(dataset[lon_dim].min()), 
            float(dataset[lon_dim].max()) + lon_bucket_size, 
            lon_bucket_size
        )
        
        # Assign new coordinates to bins
        lat_labels = lat_bins[:-1] + lat_bucket_size/2
        lon_labels = lon_bins[:-1] + lon_bucket_size/2
        
        # Create a new dataset to hold the bucketed data
        result = xr.Dataset()
        
        # Group by latitude bins
        lat_groups = dataset.groupby_bins(lat_dim, lat_bins, labels=lat_labels)
        
        # Function to compute mode (most common value)
        def compute_mode(array):
            values, counts = np.unique(array.values, return_counts=True)
            return values[np.argmax(counts)]
        
        # Process each latitude group separately
        for lat_bin, lat_group in lat_groups:
            # Group by longitude within this latitude group
            lon_groups = lat_group.groupby_bins(lon_dim, lon_bins, labels=lon_labels)
            
            # Process each longitude group
            for lon_bin, lon_group in lon_groups:
                # Apply aggregation method to this cell
                if agg_method in [AggregationMethod.MODE, AggregationMethod.MAJORITY]:
                    # Most common value (statistical mode)
                    agg_data = xr.Dataset(
                        data_vars={
                            "evt": compute_mode(lon_group.evt)
                        }
                    )
                elif agg_method == AggregationMethod.FIRST:
                    agg_data = lon_group.isel({lat_dim: 0, lon_dim: 0}, drop=True)
                elif agg_method == AggregationMethod.LAST:
                    agg_data = lon_group.isel({lat_dim: -1, lon_dim: -1}, drop=True)
                else:
                    raise ValueError(f"Unsupported aggregation method: {agg_method}")
                
                # Add new coordinates for the binned dimensions
                agg_data = agg_data.assign_coords({
                    'lat_bins': lat_bin,
                    'lon_bins': lon_bin
                })
                
                # Merge into result dataset
                if 'lat_bins' in result.dims and 'lon_bins' in result.dims:
                    # Add this cell to the existing result
                    result = xr.merge([result, agg_data])
                else:
                    # First cell, initialize the result
                    result = agg_data
        
        return result
    
    def save_dataset(self, dataset: xr.Dataset, output_path: str):
        """
        Save the processed dataset to a NetCDF file.
        
        Args:
            dataset: xarray Dataset to save
            output_path: Path to save the NetCDF file
        """
        print(f"Saving dataset to {output_path}")
        dataset.to_netcdf(output_path)
        print(f"Dataset saved to {output_path}")
    
    def cleanup(self):
        """Clean up temporary files and directories."""
        if hasattr(self, '_temp_dir'):
            self._temp_dir.cleanup()

if __name__ == "__main__":
    import sys
    
    print("LANDFIRE Processor Example")
    print("=========================")
    print("This script demonstrates the capabilities of the LandfireProcessor class.")
    print("To download and process real data, you need internet access")
    print("and the landfire Python package installed.")
    print()
    
    try:
        # Example usage
        # Bounding box for a small area in Montana
        bbox = "-107.70894965 46.56799094 -106.02718124 47.34869094"
        print(f"Using bounding box: {bbox}")
        
        # Initialize processor with local data directory
        import os
        data_dir = os.path.abspath("../data/landfire")
        os.makedirs(data_dir, exist_ok=True)
        
        # Check if landfire package is available
        try:
            import landfire
            print("The landfire package is installed. Proceeding with processing.")
            
            # Initialize the processor
            processor = LandfireProcessor(bbox=bbox, data_dir=data_dir)
            
            # Check if example data is already downloaded
            if os.path.exists(os.path.join(data_dir, "landfire_220EVT.zip")):
                print(f"\nUsing existing data file: {os.path.join(data_dir, 'landfire_220EVT.zip')}")
                processor.raw_data_path = os.path.join(data_dir, "landfire_220EVT.zip")
                
                # Attempt to extract and process with real data
                print("\nAttempting to extract data...")
                try:
                    extracted_dir = processor.extract_data()
                    print(f"Data extracted to: {extracted_dir}")
                    
                    print("\nAttempting to create dataset...")
                    dataset = processor.create_dataset()
                    print("Dataset created successfully.")
                    
                    print("\nAttempting to reproject dataset...")
                    reprojected = processor.reproject_to_latlon()
                    print("Reprojection successful.")
                    
                    print("\nAttempting to bucket spatially...")
                    bucketed = processor.bucket_spatial(lat_bucket_size=0.01, lon_bucket_size=0.01)
                    print("Spatial bucketing successful.")
                    
                    output_path = os.path.join(data_dir, "landfire_evt_bucketed.nc")
                    print(f"\nSaving processed dataset to: {output_path}")
                    processor.save_dataset(bucketed, output_path)
                    
                except Exception as e:
                    print(f"\nError during processing: {e}")
                    print("\nPlease download the LANDFIRE data using:")
                    print("processor.download_data('220EVT')")
            else:
                print("\nNo LANDFIRE data file found.")
                print("\nTo download LANDFIRE data, run the following commands:")
                print("processor = LandfireProcessor(bbox=bbox, data_dir='../data/landfire')")
                print("processor.download_data('220EVT')")
                print("processor.extract_data()")
                print("dataset = processor.create_dataset()")
                print("reprojected = processor.reproject_to_latlon()")
                print("bucketed = processor.bucket_spatial(lat_bucket_size=0.01, lon_bucket_size=0.01)")
                print("processor.save_dataset(bucketed, 'landfire_evt_bucketed.nc')")
        except ImportError:
            print("\nThe landfire package is not installed.")
            print("Install it with: pip install landfire")
            print("\nExiting.")
        
    except Exception as e:
        print(f"\nError: {str(e)}")
        sys.exit(1)