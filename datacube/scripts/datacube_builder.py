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
            try:
                # Try to see if we're dealing with cftime objects
                import cftime
                if isinstance(min_time, cftime._cftime.DatetimeNoLeap) or isinstance(min_time, np.ndarray):
                    # Create a cftime range for non-standard calendars
                    try:
                        # Convert numpy array to proper datetime if needed
                        if isinstance(min_time, np.ndarray):
                            print(f"Converting numpy time value to cftime object: {min_time}")
                            # Try to get calendar info from one of the datasets
                            calendar = None
                            units = None
                            for dataset in self.datasets.values():
                                if 'time' in dataset.coords and hasattr(dataset.time, 'attrs'):
                                    calendar = dataset.time.attrs.get('calendar', 'standard')
                                    units = dataset.time.attrs.get('units')
                                    if calendar and units:
                                        break
                            
                            if calendar and units and 'days since' in units:
                                # Extract the reference date from the units
                                ref_date = units.split('days since ')[1].split()[0]
                                # Create proper cftime objects
                                min_time = cftime.num2date(float(min_time), units=units, calendar=calendar)
                                if isinstance(max_time, np.ndarray):
                                    max_time = cftime.num2date(float(max_time), units=units, calendar=calendar)
                        
                        # Now create a time range with cftime
                        start_date = min_time
                        end_date = max_time
                        
                        # Parse the frequency to determine step size
                        if time_resolution in ['ME', 'M', '1ME', '1M']:
                            step = 1
                            # Create a sequence of monthly dates
                            times = []
                            current = start_date
                            while current <= end_date:
                                times.append(current)
                                # Add a month
                                year = current.year + (current.month // 12)
                                month = (current.month % 12) + 1
                                current = cftime.DatetimeNoLeap(year, month, 15)
                            time_range = np.array(times)
                        elif time_resolution in ['QE', 'Q', '3ME', '3M']:
                            # Create a quarterly sequence
                            times = []
                            current = start_date
                            while current <= end_date:
                                times.append(current)
                                # Add 3 months
                                year = current.year + ((current.month + 2) // 12)
                                month = ((current.month + 2) % 12) + 1
                                current = cftime.DatetimeNoLeap(year, month, 15)
                            time_range = np.array(times)
                        elif time_resolution in ['YE', 'Y', '12ME', '12M']:
                            # Create an annual sequence
                            times = []
                            current = start_date
                            while current <= end_date:
                                times.append(current)
                                # Add a year
                                current = cftime.DatetimeNoLeap(current.year + 1, current.month, 15)
                            time_range = np.array(times)
                        else:
                            # Default: use monthly
                            print(f"Warning: Unsupported time_resolution '{time_resolution}' for cftime. Using monthly.")
                            times = []
                            current = start_date
                            while current <= end_date:
                                times.append(current)
                                # Add a month
                                year = current.year + (current.month // 12)
                                month = (current.month % 12) + 1
                                current = cftime.DatetimeNoLeap(year, month, 15)
                            time_range = np.array(times)
                    except Exception as e:
                        print(f"Error creating cftime range: {e}")
                        # Fallback: create a sequence of integers for time steps
                        print("Using fallback integer time steps")
                        steps = 12  # Default to monthly (12 per year)
                        if time_resolution in ['QE', 'Q', '3ME', '3M']:
                            steps = 4  # Quarterly
                        elif time_resolution in ['YE', 'Y', '12ME', '12M']:
                            steps = 1  # Yearly
                        
                        # Create a simple range of integers
                        time_range = np.arange(0, steps * 5)  # 5 years of data
                else:
                    # Regular datetime objects
                    time_range = xr.date_range(start=min_time, end=max_time, freq=time_resolution)
            except ImportError:
                # cftime not available
                print("Warning: cftime not available. Using standard date_range.")
                try:
                    time_range = xr.date_range(start=min_time, end=max_time, freq=time_resolution)
                except Exception as e:
                    print(f"Error creating time range with standard date_range: {e}")
                    print("Using fallback integer time steps")
                    # Create a simple range of integers as fallback
                    steps = 12  # Default to monthly (12 per year)
                    if time_resolution in ['QE', 'Q', '3ME', '3M']:
                        steps = 4  # Quarterly
                    elif time_resolution in ['YE', 'Y', '12ME', '12M']:
                        steps = 1  # Yearly
                    
                    # Create a simple range of integers
                    time_range = np.arange(0, steps * 5)  # 5 years of data
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
        # Check if we're using non-standard calendar times
        try:
            import cftime
            if len(times) > 0 and isinstance(times[0], cftime._cftime.DatetimeNoLeap):
                # For non-standard calendars, we need to create a proper time coordinate
                print("Creating target grid with non-standard calendar")
                # Get the calendar and units from one of the datasets
                calendar = None
                units = None
                for dataset in self.datasets.values():
                    if 'time' in dataset.coords and hasattr(dataset.time, 'attrs'):
                        calendar = dataset.time.attrs.get('calendar')
                        units = dataset.time.attrs.get('units')
                        if calendar and units:
                            break
                
                # Create the target grid with the appropriate time encoding
                target_grid = xr.Dataset(
                    coords={
                        'lat': lats,
                        'lon': lons,
                        'time': times
                    }
                )
                
                # Add appropriate attributes to the time coordinate
                if calendar and units:
                    target_grid.time.attrs['calendar'] = calendar
                    target_grid.time.attrs['units'] = units
            else:
                # Standard datetime, create normal target grid
                target_grid = xr.Dataset(
                    coords={
                        'lat': lats,
                        'lon': lons,
                        'time': times
                    }
                )
        except ImportError:
            # cftime not available, use standard grid
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
            try:
                # Try standard interpolation
                regridded = regridded.interp(
                    lat=target_grid.lat,
                    lon=target_grid.lon,
                    method=method
                )
            except AttributeError as e:
                if "'ScipyArrayWrapper' object has no attribute 'oindex'" in str(e):
                    print("Warning: ScipyArrayWrapper issue detected. Using simple nearest neighbor approach.")
                    
                    # For each variable, create a new version with target grid coordinates
                    aligned_vars = {}
                    for var_name, data_array in regridded.data_vars.items():
                        print(f"Processing variable {var_name} with simplified approach")
                        
                        # Get the source grid coordinates
                        source_lats = regridded.lat.values
                        source_lons = regridded.lon.values
                        target_lats = target_grid.lat.values
                        target_lons = target_grid.lon.values
                        
                        # For each target grid point, find nearest source point
                        # Check if the data is time-dependent
                        if 'time' in data_array.dims:
                            # Get the time dimension size
                            time_size = data_array.sizes['time']
                            
                            # Create a 3D array for time-dependent data
                            new_data = np.zeros((time_size, len(target_lats), len(target_lons)), dtype=data_array.dtype)
                            
                            # Simple nearest neighbor approach - create a mapping from target to source
                            lat_mapping = {}
                            lon_mapping = {}
                            
                            for i, target_lat in enumerate(target_lats):
                                lat_diffs = np.abs(source_lats - target_lat)
                                lat_mapping[i] = np.argmin(lat_diffs)
                            
                            for j, target_lon in enumerate(target_lons):
                                lon_diffs = np.abs(source_lons - target_lon)
                                lon_mapping[j] = np.argmin(lon_diffs)
                            
                            # For each time step, copy the data
                            for t in range(time_size):
                                for i in range(len(target_lats)):
                                    for j in range(len(target_lons)):
                                        # Get the nearest source indices
                                        nearest_lat_idx = lat_mapping[i]
                                        nearest_lon_idx = lon_mapping[j]
                                        
                                        # Copy the data for this time point and location
                                        if data_array.dims.index('time') == 0:
                                            # Time is the first dimension
                                            new_data[t, i, j] = float(data_array.isel(time=t, lat=nearest_lat_idx, lon=nearest_lon_idx).values)
                                        else:
                                            # Time is in another position - adjust accordingly
                                            idx = [0] * len(data_array.shape)
                                            time_pos = data_array.dims.index('time')
                                            lat_pos = data_array.dims.index('lat')
                                            lon_pos = data_array.dims.index('lon')
                                            idx[time_pos] = t
                                            idx[lat_pos] = nearest_lat_idx
                                            idx[lon_pos] = nearest_lon_idx
                                            new_data[t, i, j] = float(data_array.values[tuple(idx)])
                        else:
                            # For time-independent data - 2D array
                            new_data = np.zeros((len(target_lats), len(target_lons)), dtype=data_array.dtype)
                            
                            # Simple nearest neighbor approach
                            for i, target_lat in enumerate(target_lats):
                                lat_diffs = np.abs(source_lats - target_lat)
                                nearest_lat_idx = np.argmin(lat_diffs)
                                
                                for j, target_lon in enumerate(target_lons):
                                    lon_diffs = np.abs(source_lons - target_lon)
                                    nearest_lon_idx = np.argmin(lon_diffs)
                                    
                                    # Get the value from the nearest cell (ensure it's a scalar)
                                    try:
                                        new_data[i, j] = float(data_array.isel(lat=nearest_lat_idx, lon=nearest_lon_idx).values)
                                    except (ValueError, TypeError):
                                        # If conversion to float fails, use the first element
                                        scalar_value = data_array.isel(lat=nearest_lat_idx, lon=nearest_lon_idx).values.item(0)
                                        new_data[i, j] = scalar_value
                        
                        # Create a new DataArray with the target grid
                        if 'time' in data_array.dims:
                            # For time-dependent data, create with time dimension
                            time_vals = regridded.time.values
                            aligned_vars[var_name] = xr.DataArray(
                                data=new_data,
                                dims=['time', 'lat', 'lon'],
                                coords={
                                    'time': time_vals,
                                    'lat': target_lats,
                                    'lon': target_lons
                                },
                                attrs=data_array.attrs
                            )
                        else:
                            # For time-independent data
                            aligned_vars[var_name] = xr.DataArray(
                                data=new_data,
                                dims=['lat', 'lon'],
                                coords={
                                    'lat': target_lats,
                                    'lon': target_lons
                                },
                                attrs=data_array.attrs
                            )
                    
                    # Create a new dataset with the interpolated variables
                    regridded = xr.Dataset(
                        data_vars=aligned_vars,
                        coords={
                            'lat': target_lats,
                            'lon': target_lons,
                            'time': regridded.time.values if 'time' in regridded.dims else None
                        }
                    )
                    
                    # Remove time coordinate if it's None
                    if 'time' in regridded.coords and regridded.time.values is None:
                        regridded = regridded.drop_vars('time')
                else:
                    # Re-raise the exception if it's not the expected issue
                    raise
            
            # Resample time dimension if needed
            if 'time' in regridded.dims:
                try:
                    # Try standard resampling
                    regridded = regridded.resample(time=time_resolution).nearest()
                except Exception as e:
                    print(f"Warning: Time resampling failed: {e}")
                    print("Attempting alternative time alignment")
                    
                    # If we have cftime objects, we need a different approach
                    try:
                        import cftime
                        # Check if we have non-standard calendar times
                        if (len(target_grid.time) > 0 and 
                            isinstance(target_grid.time.values[0], cftime._cftime.DatetimeNoLeap)):
                            
                            print("Aligning dataset with non-standard calendar times")
                            # Find the nearest time point for each target time
                            # This is a crude approximation - we just map each time to the nearest available
                            aligned_data = {}
                            
                            # For each target time, find closest source time
                            for i, target_time in enumerate(target_grid.time.values):
                                # Find closest source time (very simple approach)
                                diffs = []
                                for j, source_time in enumerate(regridded.time.values):
                                    # Calculate difference in days (approximate)
                                    try:
                                        diff = abs((target_time.year - source_time.year) * 365 + 
                                                  (target_time.month - source_time.month) * 30 + 
                                                  (target_time.day - source_time.day))
                                    except AttributeError:
                                        # Fallback if we can't compare directly
                                        diff = abs(i - j)  # Just use index difference as approximation
                                    diffs.append((j, diff))
                                
                                # Get the index with minimum difference
                                closest_idx = min(diffs, key=lambda x: x[1])[0]
                                
                                # Select data at this time and add to our aligned data
                                for var in regridded.data_vars:
                                    if var not in aligned_data:
                                        # Initialize with NaN array
                                        shape = list(regridded[var].shape)
                                        shape[0] = len(target_grid.time)  # Replace time dimension
                                        aligned_data[var] = np.full(shape, np.nan)
                                    
                                    # Copy data for this time point
                                    time_dim_pos = list(regridded[var].dims).index('time') if 'time' in regridded[var].dims else 0
                                    if time_dim_pos == 0:
                                        # Time is the first dimension
                                        aligned_data[var][i] = regridded[var].isel(time=closest_idx).values
                                    else:
                                        # Time is in another position
                                        idx = [slice(None)] * len(regridded[var].dims)
                                        idx[time_dim_pos] = closest_idx
                                        idx_target = [slice(None)] * len(regridded[var].dims)
                                        idx_target[time_dim_pos] = i
                                        aligned_data[var][tuple(idx_target)] = regridded[var][tuple(idx)].values
                            
                            # Create a new dataset with aligned data
                            aligned_ds = xr.Dataset(
                                data_vars={var: (regridded[var].dims, aligned_data[var]) for var in aligned_data},
                                coords={
                                    'lat': regridded.lat,
                                    'lon': regridded.lon,
                                    'time': target_grid.time
                                }
                            )
                            
                            # Copy attributes
                            for var in aligned_ds.data_vars:
                                if var in regridded.data_vars:
                                    aligned_ds[var].attrs.update(regridded[var].attrs)
                            
                            # Replace regridded with aligned dataset
                            regridded = aligned_ds
                        else:
                            # For standard calendars but time resampling failed
                            # Just use the original regridded dataset without time resampling
                            print("Using original time coordinates without resampling")
                    except ImportError:
                        # cftime not available, skip time resampling
                        print("cftime not available, skipping time resampling")
            
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