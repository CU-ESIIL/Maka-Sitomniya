#!/usr/bin/env python
"""
CMIP Dataset Processor

This module provides functionality to process CMIP climate data, allowing
for flexible spatial and temporal bucketing with various aggregation methods.

The CMIPProcessor class can:
1. Load CMIP climate data from NetCDF files
2. Determine native spatial and temporal resolutions
3. Apply spatial bucketing (aggregation) with custom resolutions
4. Apply temporal bucketing with custom time periods
5. Process data into standardized datacubes with multiple aggregation options
6. Save processed datacubes to NetCDF files

Usage:
    processor = CMIPProcessor(data_path)
    
    # Get native resolutions
    spatial_res = processor.get_spatial_resolution()
    temporal_res = processor.get_temporal_resolution()
    
    # Process to datacube with custom buckets
    datacube = processor.process_to_datacube(
        lat_bucket_size=0.5,
        lon_bucket_size=0.5,
        time_bucket_size='3ME',
        spatial_agg_method=AggregationMethod.MEAN,
        temporal_agg_method=AggregationMethod.MEAN
    )
    
    # Save the processed datacube
    processor.save_datacube(datacube, output_path)
"""

import os
import numpy as np
import xarray as xr
import tempfile
from datetime import datetime
from enum import Enum
from typing import Optional, Union, List, Tuple

class AggregationMethod(Enum):
    """
    Enumeration of supported aggregation methods for bucketing data.
    
    Available methods:
    - MEAN: Average value within the bucket
    - MEDIAN: Median value within the bucket
    - MAX: Maximum value within the bucket
    - MIN: Minimum value within the bucket
    - SUM: Sum of all values within the bucket
    - FIRST: First value encountered in the bucket
    - LAST: Last value encountered in the bucket
    - STD: Standard deviation of values within the bucket
    - VAR: Variance of values within the bucket
    """
    MEAN = "mean"
    MEDIAN = "median"
    MAX = "max"
    MIN = "min"
    SUM = "sum"
    FIRST = "first"
    LAST = "last"
    STD = "std"
    VAR = "var"

class CMIPProcessor:
    """
    Processor for CMIP climate data.
    
    This class handles loading, processing, and bucketing CMIP NetCDF data
    with customizable spatial and temporal resolutions.
    """
    
    def __init__(self, data_path: str):
        """
        Initialize the CMIP processor.
        
        Args:
            data_path: Path to the CMIP NetCDF data file
        """
        self.data_path = data_path
        self.dataset = None
        self._load_dataset()
    
    def _load_dataset(self):
        """Load the CMIP dataset from the specified path."""
        if not os.path.exists(self.data_path):
            raise FileNotFoundError(f"Data file not found: {self.data_path}")
        
        try:
            # Try to open dataset with default settings
            self.dataset = xr.open_dataset(self.data_path)
        except ValueError as e:
            if "unable to decode time units" in str(e) or "calendar" in str(e):
                # If time decoding fails due to calendar issues, try with decode_times=False
                print("Warning: Non-standard calendar detected. Loading with decode_times=False.")
                try:
                    # Try to import cftime
                    import cftime
                    print("Using cftime for non-standard calendar.")
                    self.dataset = xr.open_dataset(self.data_path, use_cftime=True)
                except ImportError:
                    print("cftime not available. Loading without decoding times.")
                    self.dataset = xr.open_dataset(self.data_path, decode_times=False)
            else:
                # Re-raise if it's a different ValueError
                raise
                
        print(f"Loaded dataset with dimensions: {self.dataset.dims}")
        print(f"Variables: {list(self.dataset.data_vars)}")
    
    def get_spatial_resolution(self) -> Tuple[float, float]:
        """
        Get the native spatial resolution of the dataset.
        
        Returns:
            Tuple of (latitude_resolution, longitude_resolution) in degrees
        """
        if 'lat' in self.dataset.dims and 'lon' in self.dataset.dims:
            lat_res = abs(float(self.dataset.lat[1] - self.dataset.lat[0]))
            lon_res = abs(float(self.dataset.lon[1] - self.dataset.lon[0]))
            return (lat_res, lon_res)
        else:
            # Check for alternative coordinate names
            lat_dim = next((d for d in self.dataset.dims if 'lat' in d.lower()), None)
            lon_dim = next((d for d in self.dataset.dims if 'lon' in d.lower()), None)
            
            if lat_dim and lon_dim:
                lat_res = abs(float(self.dataset[lat_dim][1] - self.dataset[lat_dim][0]))
                lon_res = abs(float(self.dataset[lon_dim][1] - self.dataset[lon_dim][0]))
                return (lat_res, lon_res)
            else:
                raise ValueError("Could not determine spatial dimensions in dataset")
    
    def get_temporal_resolution(self) -> str:
        """
        Get the native temporal resolution of the dataset.
        
        Returns:
            String representing temporal resolution (e.g., 'monthly', 'daily')
        """
        if 'time' in self.dataset.dims:
            # Check time difference between first two time steps
            if len(self.dataset.time) > 1:
                time_diff = self.dataset.time[1] - self.dataset.time[0]
                days = time_diff.values.astype('timedelta64[D]').astype(int)
                
                if days == 1:
                    return "daily"
                elif 28 <= days <= 31:
                    return "monthly"
                elif 365 <= days <= 366:
                    return "yearly"
                else:
                    return f"{days}-day"
            else:
                return "single-timepoint"
        else:
            raise ValueError("No time dimension found in dataset")
    
    def bucket_spatial(self, 
                      lat_bucket_size: float, 
                      lon_bucket_size: float,
                      agg_method: AggregationMethod = AggregationMethod.MEAN,
                      variables: Optional[List[str]] = None) -> xr.Dataset:
        """
        Bucket the data into specified spatial resolution.
        
        Args:
            lat_bucket_size: Size of latitude buckets in degrees
            lon_bucket_size: Size of longitude buckets in degrees
            agg_method: Method to aggregate data within buckets
            variables: Optional list of variables to process (defaults to all)
            
        Returns:
            Dataset with bucketed spatial dimensions
        """
        # Use a copy of the dataset
        dataset = self.dataset
        
        # Filter variables if specified
        if variables:
            # Filter to include only the variables that exist
            existing_vars = [var for var in variables if var in dataset.data_vars]
            if existing_vars:
                dataset = dataset[existing_vars]
        
        # Identify lat/lon dimensions
        lat_dim = next((d for d in dataset.dims if 'lat' in d.lower()), 'lat')
        lon_dim = next((d for d in dataset.dims if 'lon' in d.lower()), 'lon')
        
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
        
        # Create a new dataset with the binned coordinates
        result = xr.Dataset()
        
        # First group by latitude bins
        lat_groups = dataset.groupby_bins(lat_dim, lat_bins, labels=lat_labels)
        
        # Process each latitude group separately
        for lat_bin, lat_group in lat_groups:
            # Group by longitude within this latitude group
            lon_groups = lat_group.groupby_bins(lon_dim, lon_bins, labels=lon_labels)
            
            # Process each longitude group
            for lon_bin, lon_group in lon_groups:
                # Apply aggregation method to this cell
                if agg_method == AggregationMethod.MEAN:
                    agg_data = lon_group.mean(dim=[lat_dim, lon_dim])
                elif agg_method == AggregationMethod.MEDIAN:
                    agg_data = lon_group.median(dim=[lat_dim, lon_dim])
                elif agg_method == AggregationMethod.MAX:
                    agg_data = lon_group.max(dim=[lat_dim, lon_dim])
                elif agg_method == AggregationMethod.MIN:
                    agg_data = lon_group.min(dim=[lat_dim, lon_dim])
                elif agg_method == AggregationMethod.SUM:
                    agg_data = lon_group.sum(dim=[lat_dim, lon_dim])
                elif agg_method == AggregationMethod.FIRST:
                    agg_data = lon_group.isel({lat_dim: 0, lon_dim: 0}, drop=True)
                elif agg_method == AggregationMethod.LAST:
                    agg_data = lon_group.isel({lat_dim: -1, lon_dim: -1}, drop=True)
                elif agg_method == AggregationMethod.STD:
                    agg_data = lon_group.std(dim=[lat_dim, lon_dim])
                elif agg_method == AggregationMethod.VAR:
                    agg_data = lon_group.var(dim=[lat_dim, lon_dim])
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
    
    def bucket_temporal(self, 
                       bucket_size: str,
                       agg_method: AggregationMethod = AggregationMethod.MEAN,
                       variables: Optional[List[str]] = None) -> xr.Dataset:
        """
        Bucket the data into specified temporal resolution.
        
        Args:
            bucket_size: Size of time buckets (e.g., 'ME' for month end, 'YE' for year end, '10D')
                Use 'ME' for monthly, 'QE' for quarterly, 'YE' for yearly (not 'M', 'Q', 'Y')
            agg_method: Method to aggregate data within buckets
            variables: Optional list of variables to process (defaults to all)
            
        Returns:
            Dataset with bucketed temporal dimension
        """
        # Use a copy of the dataset
        dataset = self.dataset
        
        # Filter variables if specified
        if variables:
            # Filter to include only the variables that exist
            existing_vars = [var for var in variables if var in dataset.data_vars]
            if existing_vars:
                dataset = dataset[existing_vars]
        
        # Fix deprecated time frequencies
        if bucket_size == 'M':
            bucket_size = 'ME'  # Month end instead of deprecated 'M'
        elif bucket_size == 'Q':
            bucket_size = 'QE'  # Quarter end instead of deprecated 'Q'
        elif bucket_size == 'Y':
            bucket_size = 'YE'  # Year end instead of deprecated 'Y'
        elif bucket_size == '3M':
            bucket_size = '3ME'  # 3-month end instead of deprecated '3M'
        
        # Check if time is properly decoded
        if not np.issubdtype(dataset.time.dtype, np.datetime64):
            print("Warning: Time coordinate is not decoded as datetime. Attempting to create time bins manually.")
            
            # Get the number of time steps based on the specified bucket size
            if bucket_size in ['ME', 'M', '1ME', '1M']:
                # Monthly bucketing - should get roughly 1/1 of original steps
                buckets = 1
            elif bucket_size in ['QE', 'Q', '3ME', '3M']:
                # Quarterly bucketing - should get roughly 1/3 of original steps
                buckets = 3
            elif bucket_size in ['YE', 'Y', '12ME', '12M']:
                # Yearly bucketing - should get roughly 1/12 of original steps
                buckets = 12
            else:
                # For other sizes, default to no reduction
                print(f"Warning: Unsupported bucket size '{bucket_size}' for undecoded time. Using original time steps.")
                buckets = 1
            
            # Create time bins manually
            time_steps = len(dataset.time)
            new_time_steps = time_steps // buckets
            if new_time_steps == 0:
                new_time_steps = 1
            
            # Create a new dataset with aggregated time dimension
            result = dataset.isel(time=slice(0, None, buckets))
            
            return result
        else:
            # Group by time using resample if time is properly decoded
            try:
                grouped = dataset.resample(time=bucket_size)
            except TypeError as e:
                if "Only valid with DatetimeIndex" in str(e):
                    print("Warning: Time resampling failed. Using simple stride-based aggregation.")
                    
                    # Use stride-based aggregation as a fallback
                    if bucket_size in ['ME', 'M', '1ME', '1M']:
                        buckets = 1
                    elif bucket_size in ['QE', 'Q', '3ME', '3M']:
                        buckets = 3
                    elif bucket_size in ['YE', 'Y', '12ME', '12M']:
                        buckets = 12
                    else:
                        print(f"Warning: Unsupported bucket size '{bucket_size}'. Using monthly bucket.")
                        buckets = 1
                    
                    # Create a new dataset with aggregated time dimension
                    result = dataset.isel(time=slice(0, None, buckets))
                    return result
                else:
                    raise
        
        # Apply aggregation method
        if agg_method == AggregationMethod.MEAN:
            return grouped.mean()
        elif agg_method == AggregationMethod.MEDIAN:
            return grouped.median()
        elif agg_method == AggregationMethod.MAX:
            return grouped.max()
        elif agg_method == AggregationMethod.MIN:
            return grouped.min()
        elif agg_method == AggregationMethod.SUM:
            return grouped.sum()
        elif agg_method == AggregationMethod.FIRST:
            return grouped.first()
        elif agg_method == AggregationMethod.LAST:
            return grouped.last()
        elif agg_method == AggregationMethod.STD:
            return grouped.std()
        elif agg_method == AggregationMethod.VAR:
            return grouped.var()
        else:
            raise ValueError(f"Unsupported aggregation method: {agg_method}")
    
    def process_to_datacube(self,
                          lat_bucket_size: Optional[float] = None,
                          lon_bucket_size: Optional[float] = None,
                          time_bucket_size: Optional[str] = None,
                          spatial_agg_method: AggregationMethod = AggregationMethod.MEAN,
                          temporal_agg_method: AggregationMethod = AggregationMethod.MEAN,
                          variables: Optional[List[str]] = None) -> xr.Dataset:
        """
        Process the dataset to create a datacube with specified bucketing.
        
        Args:
            lat_bucket_size: Size of latitude buckets in degrees (optional)
            lon_bucket_size: Size of longitude buckets in degrees (optional)
            time_bucket_size: Size of time buckets (e.g., 'ME' for month end, 'YE' for year end) (optional)
            spatial_agg_method: Method to aggregate data within spatial buckets
            temporal_agg_method: Method to aggregate data within temporal buckets
            variables: List of variables to include (uses all by default)
            
        Returns:
            Processed datacube as xarray Dataset
        """
        # Start with the full dataset
        dataset = self.dataset
        
        # Subset to specified variables if provided
        if variables:
            # Filter to include only the variables that exist in the dataset
            existing_vars = [var for var in variables if var in dataset.data_vars]
            dataset = dataset[existing_vars]
        
        # Apply the processing steps in a specific order to ensure proper handling
        processed_dataset = dataset
        
        # Process temporal bucketing first if specified
        if time_bucket_size is not None:
            print("Applying temporal bucketing...")
            try:
                processed_dataset = self.bucket_temporal(
                    time_bucket_size,
                    temporal_agg_method,
                    variables
                )
                print(f"Temporal bucketing complete. New dimensions: {processed_dataset.dims}")
            except Exception as e:
                print(f"Warning: Temporal bucketing failed: {e}")
                print("Skipping temporal bucketing")
        
        # Then apply spatial bucketing if specified
        if lat_bucket_size is not None and lon_bucket_size is not None:
            print("Applying spatial bucketing...")
            try:
                # Try using the standard spatial bucketing
                processed_dataset = self.bucket_spatial(
                    lat_bucket_size, 
                    lon_bucket_size,
                    spatial_agg_method,
                    variables
                )
                print(f"Spatial bucketing complete. New dimensions: {processed_dataset.dims}")
            except Exception as e:
                print(f"Warning: Advanced spatial bucketing failed: {e}")
                print("Falling back to simplified spatial aggregation")
                
                # Get the current dataset (already temporally bucketed if applicable)
                ds = processed_dataset
                
                # Identify lat/lon dimensions
                lat_dim = next((d for d in ds.dims if 'lat' in d.lower()), 'lat')
                lon_dim = next((d for d in ds.dims if 'lon' in d.lower()), 'lon')
                
                # Calculate stride for lat/lon to approximate the requested bucket sizes
                lat_res, lon_res = self.get_spatial_resolution()
                lat_stride = max(1, int(lat_bucket_size / lat_res))
                lon_stride = max(1, int(lon_bucket_size / lon_res))
                
                print(f"Using strides: lat={lat_stride}, lon={lon_stride}")
                
                # Create a coarser resolution dataset using slicing
                processed_dataset = ds.isel({
                    lat_dim: slice(0, None, lat_stride),
                    lon_dim: slice(0, None, lon_stride)
                })
                
                print(f"Reduced resolution from {ds.dims} to {processed_dataset.dims}")
        
        return processed_dataset
    
    def save_datacube(self, dataset: xr.Dataset, output_path: str):
        """
        Save the processed datacube to a NetCDF file.
        
        Args:
            dataset: Processed xarray Dataset
            output_path: Path to save the NetCDF file
        """
        dataset.to_netcdf(output_path)
        print(f"Saved datacube to {output_path}")

if __name__ == "__main__":
    # Check if the example data file exists
    import os
    import sys
    
    data_path = "./data/macav2metdata_huss_CCSM4_r6i1p1_rcp45_2021_2025_CONUS_monthly.nc"
    
    if not os.path.exists(data_path):
        # Try alternative path in case script is run from project root
        alt_path = "../data/macav2metdata_huss_CCSM4_r6i1p1_rcp45_2021_2025_CONUS_monthly.nc"
        if os.path.exists(alt_path):
            data_path = alt_path
        else:
            print("Example data file not found.")
            print(f"To run this example, place CMIP data at: {data_path}")
            print("or adjust the data_path variable to point to an existing file.")
            print("Make sure you run this script from the datacube directory.")
            sys.exit(1)
    
    # If data exists, proceed with example processing
    processor = CMIPProcessor(data_path)
    
    # Get native resolutions
    spatial_res = processor.get_spatial_resolution()
    temporal_res = processor.get_temporal_resolution()
    print(f"Native spatial resolution: {spatial_res} degrees")
    print(f"Native temporal resolution: {temporal_res}")
    
    # Process to datacube
    datacube = processor.process_to_datacube(
        lat_bucket_size=0.5,  # 0.5 degree lat buckets
        lon_bucket_size=0.5,  # 0.5 degree lon buckets
        time_bucket_size='3ME',  # 3-month (quarterly) buckets
        spatial_agg_method=AggregationMethod.MEAN,
        temporal_agg_method=AggregationMethod.MEAN
    )
    
    # Save the processed datacube
    output_path = "./data/processed/processed_cmip_datacube.nc"
    print(f"Saving processed datacube to: {output_path}")
    
    # Make sure the output directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    processor.save_datacube(datacube, output_path)
    print("Processing complete!")