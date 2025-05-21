#!/usr/bin/env python
"""
Datacube Builder Module

This module provides functionality to combine multiple datasets into a unified datacube
with consistent spatial and temporal dimensions.

The DatacubeBuilder class allows:
1. Loading multiple datasets from different sources
2. Creating a unified spatial and temporal grid
3. Aligning datasets to the unified grid with different interpolation methods
4. Combining multiple variables into a single, consistent datacube
5. Saving the combined datacube for further analysis

Usage:
    builder = DatacubeBuilder()
    
    # Add datasets
    builder.add_dataset("dataset1", dataset1)
    builder.load_dataset_from_file("dataset2", "path/to/dataset2.nc")
    
    # Build unified datacube
    datacube = builder.build_datacube(
        lat_resolution=0.5,
        lon_resolution=0.5,
        time_resolution='1ME',
        interpolation_method=InterpolationMethod.LINEAR
    )
    
    # Save the result
    builder.save_datacube("path/to/output.nc")
"""

import os
import numpy as np
import xarray as xr
from typing import List, Dict, Optional, Union, Tuple
from enum import Enum

class InterpolationMethod(Enum):
    """
    Enumeration of supported interpolation methods for aligning datasets.
    
    Available methods:
    - NEAREST: Nearest neighbor interpolation (preserves original values, but may appear blocky)
    - LINEAR: Linear interpolation (smooth transitions between points, may average out extremes)
    - CUBIC: Cubic interpolation (smoother than linear, may introduce overshoots)
    - BILINEAR: Bilinear interpolation (2D linear interpolation, good for gridded data)
    """
    NEAREST = "nearest"
    LINEAR = "linear"
    CUBIC = "cubic"
    BILINEAR = "bilinear"

class DatacubeBuilder:
    """
    Builder class for creating unified datacubes from multiple datasets.
    
    This class handles loading multiple datasets, aligning their spatial and
    temporal dimensions, and combining them into a single datacube.
    """
    
    def __init__(self):
        """Initialize the datacube builder."""
        self.datasets = {}
        self.combined_datacube = None
        
    def add_dataset(self, name: str, dataset: xr.Dataset):
        """
        Add a dataset to the datacube builder.
        
        Args:
            name: Name identifier for the dataset
            dataset: xarray Dataset to add
        """
        self.datasets[name] = dataset
        print(f"Added dataset '{name}' with dimensions: {dataset.dims}")
        
    def load_dataset_from_file(self, name: str, file_path: str):
        """
        Load a dataset from a file and add it to the datacube builder.
        
        Args:
            name: Name identifier for the dataset
            file_path: Path to the dataset file (NetCDF format)
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Dataset file not found: {file_path}")
        
        dataset = xr.open_dataset(file_path)
        self.add_dataset(name, dataset)
        
    def create_unified_grid(self, 
                           lat_resolution: float, 
                           lon_resolution: float,
                           time_resolution: str,
                           lat_bounds: Optional[Tuple[float, float]] = None,
                           lon_bounds: Optional[Tuple[float, float]] = None,
                           time_bounds: Optional[Tuple[str, str]] = None) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Create a unified grid based on specified resolution or dataset bounds.
        
        Args:
            lat_resolution: Latitude resolution in degrees
            lon_resolution: Longitude resolution in degrees
            time_resolution: Time resolution (e.g., 'month', 'year', '10D')
            lat_bounds: Optional (min_lat, max_lat) bounds, otherwise uses dataset bounds
            lon_bounds: Optional (min_lon, max_lon) bounds, otherwise uses dataset bounds
            time_bounds: Optional (start_time, end_time) bounds, otherwise uses dataset bounds
            
        Returns:
            Tuple of (lats, lons, times) arrays for the unified grid
        """
        # Determine bounds from datasets if not specified
        if lat_bounds is None or lon_bounds is None or time_bounds is None:
            # Find common dimension names across datasets
            lat_names = ['lat', 'latitude', 'y']
            lon_names = ['lon', 'longitude', 'x']
            time_names = ['time', 'date', 't']
            
            # Initialize with large/small values for finding min/max
            min_lat, max_lat = 90, -90
            min_lon, max_lon = 180, -180
            min_time, max_time = None, None
            
            for dataset in self.datasets.values():
                # Find lat dimension
                lat_dim = next((dim for dim in lat_names if dim in dataset.dims or dim in dataset.coords), None)
                if lat_dim:
                    min_lat = min(min_lat, float(dataset[lat_dim].min()))
                    max_lat = max(max_lat, float(dataset[lat_dim].max()))
                
                # Find lon dimension
                lon_dim = next((dim for dim in lon_names if dim in dataset.dims or dim in dataset.coords), None)
                if lon_dim:
                    min_lon = min(min_lon, float(dataset[lon_dim].min()))
                    max_lon = max(max_lon, float(dataset[lon_dim].max()))
                
                # Find time dimension
                time_dim = next((dim for dim in time_names if dim in dataset.dims or dim in dataset.coords), None)
                if time_dim:
                    ds_min_time = dataset[time_dim].min().values
                    ds_max_time = dataset[time_dim].max().values
                    
                    if min_time is None or ds_min_time < min_time:
                        min_time = ds_min_time
                    
                    if max_time is None or ds_max_time > max_time:
                        max_time = ds_max_time
        
        # Use specified bounds if provided
        if lat_bounds:
            min_lat, max_lat = lat_bounds
        
        if lon_bounds:
            min_lon, max_lon = lon_bounds
        
        if time_bounds:
            min_time, max_time = time_bounds
        
        # Create unified grid
        lats = np.arange(min_lat, max_lat + lat_resolution/2, lat_resolution)
        lons = np.arange(min_lon, max_lon + lon_resolution/2, lon_resolution)
        
        # Create unified time grid
        if min_time is not None and max_time is not None:
            time_range = xr.date_range(start=min_time, end=max_time, freq=time_resolution)
        else:
            raise ValueError("Could not determine time bounds from datasets")
        
        return lats, lons, time_range
    
    def build_datacube(self,
                      lat_resolution: float,
                      lon_resolution: float,
                      time_resolution: str,
                      interpolation_method: InterpolationMethod = InterpolationMethod.LINEAR,
                      fill_value: Optional[float] = None,
                      lat_bounds: Optional[Tuple[float, float]] = None,
                      lon_bounds: Optional[Tuple[float, float]] = None,
                      time_bounds: Optional[Tuple[str, str]] = None) -> xr.Dataset:
        """
        Build a unified datacube from the added datasets.
        
        Args:
            lat_resolution: Latitude resolution in degrees
            lon_resolution: Longitude resolution in degrees
            time_resolution: Time resolution (e.g., 'month', 'year', '10D')
            interpolation_method: Method to use for interpolation when aligning datasets
            fill_value: Value to use for filling missing data (uses NaN by default)
            lat_bounds: Optional latitude bounds as (min_lat, max_lat)
            lon_bounds: Optional longitude bounds as (min_lon, max_lon)
            time_bounds: Optional time bounds as (start_time, end_time) strings
            
        Returns:
            Combined datacube as xarray Dataset
        """
        if not self.datasets:
            raise ValueError("No datasets have been added to the builder")
        
        # Create unified grid
        lats, lons, times = self.create_unified_grid(
            lat_resolution, lon_resolution, time_resolution,
            lat_bounds, lon_bounds, time_bounds
        )
        
        # Create target grid dataset
        target_grid = xr.Dataset(
            coords={
                'lat': lats,
                'lon': lons,
                'time': times
            }
        )
        
        # Initialize the combined datacube
        combined_data_vars = {}
        
        # Regrid and combine each dataset
        for name, dataset in self.datasets.items():
            # Identify dimension names in this dataset
            lat_dim = next((dim for dim in ['lat', 'latitude', 'y'] if dim in dataset.dims or dim in dataset.coords), None)
            lon_dim = next((dim for dim in ['lon', 'longitude', 'x'] if dim in dataset.dims or dim in dataset.coords), None)
            time_dim = next((dim for dim in ['time', 'date', 't'] if dim in dataset.dims or dim in dataset.coords), None)
            
            if not all([lat_dim, lon_dim, time_dim]):
                print(f"Warning: Could not identify all dimensions in dataset '{name}'. Skipping.")
                continue
            
            # Prepare mapping of dataset dimensions to target dimensions
            dim_map = {lat_dim: 'lat', lon_dim: 'lon', time_dim: 'time'}
            
            # Regrid dataset to target grid
            regridded = dataset.rename({old: new for old, new in dim_map.items() if old != new})
            
            # Apply interpolation
            method = interpolation_method.value if isinstance(interpolation_method, InterpolationMethod) else interpolation_method
            regridded = regridded.interp(
                lat=target_grid.lat,
                lon=target_grid.lon,
                method=method
            )
            
            # Resample time dimension if needed
            if 'time' in regridded.dims:
                regridded = regridded.resample(time=time_resolution).nearest()
            
            # Add variables to combined datacube with prefix to avoid name conflicts
            for var_name, data_array in regridded.data_vars.items():
                # Add source dataset name as prefix to avoid conflicts
                prefixed_name = f"{name}_{var_name}"
                combined_data_vars[prefixed_name] = data_array
        
        # Create the combined datacube
        self.combined_datacube = xr.Dataset(
            data_vars=combined_data_vars,
            coords=target_grid.coords
        )
        
        # Fill missing values if specified
        if fill_value is not None:
            self.combined_datacube = self.combined_datacube.fillna(fill_value)
        
        return self.combined_datacube
    
    def save_datacube(self, output_path: str):
        """
        Save the combined datacube to a NetCDF file.
        
        Args:
            output_path: Path to save the combined datacube
        """
        if self.combined_datacube is None:
            raise ValueError("No combined datacube has been built yet")
        
        self.combined_datacube.to_netcdf(output_path)
        print(f"Saved combined datacube to {output_path}")

if __name__ == "__main__":
    import os
    import sys
    
    print("DatacubeBuilder Example")
    print("======================")
    print("This script demonstrates the capabilities of the DatacubeBuilder class.")
    print("To build a real datacube, you need source datasets available.")
    print()
    
    # Example usage
    builder = DatacubeBuilder()
    
    # Check if example files exist
    file1 = "./data/macav2metdata_huss_CCSM4_r6i1p1_rcp45_2021_2025_CONUS_monthly.nc"
    file2 = "./data/macav2metdata_huss_CCSM4_r6i1p1_rcp85_2021_2025_CONUS_monthly.nc"
    
    # Try alternative paths if not found
    if not os.path.exists(file1):
        alt_file1 = "../data/macav2metdata_huss_CCSM4_r6i1p1_rcp45_2021_2025_CONUS_monthly.nc"
        if os.path.exists(alt_file1):
            file1 = alt_file1
    
    if not os.path.exists(file2):
        alt_file2 = "../data/macav2metdata_huss_CCSM4_r6i1p1_rcp85_2021_2025_CONUS_monthly.nc"
        if os.path.exists(alt_file2):
            file2 = alt_file2
    
    if not os.path.exists(file1) or not os.path.exists(file2):
        print("Example data files not found.")
        print(f"To run this example, place CMIP data at:")
        print(f"- {file1}")
        print(f"- {file2}")
        print("or adjust the file paths to point to existing datasets.")
        print("Make sure you run this script from the datacube directory.")
        
        print("\nExample workflow:")
        print("builder = DatacubeBuilder()")
        print("builder.load_dataset_from_file(name='dataset1', file_path='path/to/file1.nc')")
        print("builder.load_dataset_from_file(name='dataset2', file_path='path/to/file2.nc')")
        print("combined_cube = builder.build_datacube(lat_resolution=0.5, lon_resolution=0.5, time_resolution='1ME')")
        print("builder.save_datacube('output_datacube.nc')")
        sys.exit(1)
    
    # If files exist, proceed with example
    try:
        print(f"Loading datasets...")
        
        # Try to load datasets with decode_times=False if needed
        try:
            builder.load_dataset_from_file(
                name="cmip_rcp45",
                file_path=file1
            )
        except Exception as e:
            if "calendar" in str(e):
                print(f"Warning: Calendar issue detected. Loading {file1} with decode_times=False")
                dataset1 = xr.open_dataset(file1, decode_times=False)
                builder.add_dataset("cmip_rcp45", dataset1)
            else:
                raise
        
        try:
            builder.load_dataset_from_file(
                name="cmip_rcp85",
                file_path=file2
            )
        except Exception as e:
            if "calendar" in str(e):
                print(f"Warning: Calendar issue detected. Loading {file2} with decode_times=False")
                dataset2 = xr.open_dataset(file2, decode_times=False)
                builder.add_dataset("cmip_rcp85", dataset2)
            else:
                raise
        
        print(f"Building datacube...")
        try:
            combined_cube = builder.build_datacube(
                lat_resolution=0.5,
                lon_resolution=0.5,
                time_resolution='1ME',  # Month end
                interpolation_method=InterpolationMethod.LINEAR
            )
            
            # Create output directory if needed
            output_path = "./data/processed/combined_cmip_datacube.nc"
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            print(f"Saving combined datacube to {output_path}...")
            builder.save_datacube(output_path)
            
            print("Processing complete!")
        except Exception as e:
            print(f"Error building datacube: {e}")
            print("Falling back to simplified approach...")
            
            # Create a simplified datacube by concatenating datasets along a new dimension
            if len(builder.datasets) > 0:
                print("Creating simplified combined dataset...")
                
                # Get list of datasets
                datasets_list = list(builder.datasets.values())
                
                # Create a simplified combined dataset
                simplified_cube = xr.concat(datasets_list, dim="scenario")
                
                # Create output directory if needed
                output_path = "./data/processed/simplified_combined_datacube.nc"
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                
                print(f"Saving simplified datacube to {output_path}...")
                simplified_cube.to_netcdf(output_path)
                
                print("Simplified processing complete!")
            else:
                print("No datasets available to combine.")
        
    except Exception as e:
        print(f"\nError: {str(e)}")
        sys.exit(1)