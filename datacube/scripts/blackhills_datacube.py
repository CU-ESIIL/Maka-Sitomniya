#!/usr/bin/env python
"""
Black Hills Datacube Builder

This script creates a complete datacube for the Black Hills region, combining
LANDFIRE vegetation data and CMIP climate data.

Usage:
    python blackhills_datacube.py [--output OUTPUT] [--resolution RESOLUTION]

Example:
    python blackhills_datacube.py --output data/blackhills_datacube.nc --resolution 0.01
"""

import os
import sys
import argparse
import xarray as xr
import numpy as np
from datetime import datetime

# Add parent directory to path to import config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

# Import processors
from cmip_processor import CMIPProcessor, AggregationMethod as CMIPAggregation
from landfire_processor import LandfireProcessor, AggregationMethod as LandfireAggregation
from datacube_builder import DatacubeBuilder, InterpolationMethod

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Build a complete datacube for the Black Hills region")
    
    parser.add_argument(
        "--output", 
        type=str, 
        default=os.path.join(config.OUTPUTS_DIR, "blackhills_datacube.nc"),
        help="Output path for the created datacube"
    )
    
    parser.add_argument(
        "--resolution", 
        type=float, 
        default=0.01,  # approximately 1km
        help="Spatial resolution in degrees for the datacube"
    )
    
    parser.add_argument(
        "--temp-resolution", 
        type=str, 
        default="ME",  # Month end
        help="Temporal resolution for the datacube (e.g., 'ME' for monthly, 'QE' for quarterly)"
    )
    
    return parser.parse_args()

def process_landfire_data(resolution):
    """
    Process LANDFIRE data for the Black Hills region.
    
    Args:
        resolution: Spatial resolution in degrees
        
    Returns:
        Processed LANDFIRE dataset
    """
    print(f"\n--- Processing LANDFIRE Vegetation Data ---")
    
    # Initialize the processor with Black Hills bounding box
    processor = LandfireProcessor(
        bbox=config.BLACK_HILLS_BBOX_STRING,
        data_dir=config.LANDFIRE_CONFIG["data_dir"]
    )
    
    # Check if data exists already
    evt_layer = config.LANDFIRE_CONFIG["layers"]["evt"]
    zip_path = os.path.join(config.LANDFIRE_CONFIG["data_dir"], f"landfire_{evt_layer}.zip")
    
    if os.path.exists(zip_path):
        print(f"Using existing LANDFIRE data file: {zip_path}")
        processor.raw_data_path = zip_path
    else:
        # Download EVT data
        print(f"Downloading LANDFIRE {evt_layer} data...")
        try:
            processor.download_data(evt_layer)
        except Exception as e:
            print(f"Error downloading LANDFIRE data: {e}")
            raise FileNotFoundError(f"Could not download or find LANDFIRE {evt_layer} data")
    
    # Extract and process data
    processor.extract_data()
    dataset = processor.create_dataset()
    print(f"Dataset created with dimensions: {dataset.dims}")
    
    # Apply spatial bucketing with MODE aggregation for categorical data
    print(f"Applying spatial bucketing with resolution {resolution}°...")
    bucketed = processor.bucket_spatial(
        lat_bucket_size=resolution,
        lon_bucket_size=resolution,
        agg_method=LandfireAggregation.MODE
    )
    
    print(f"LANDFIRE processing complete. Output shape: {bucketed.dims}")
    return bucketed

def process_cmip_data(resolution, temporal_resolution):
    """
    Process CMIP climate data for the Black Hills region.
    
    Args:
        resolution: Spatial resolution in degrees
        temporal_resolution: Temporal resolution (e.g., 'ME', '3ME')
        
    Returns:
        Processed CMIP dataset
    """
    print(f"\n--- Processing CMIP Climate Data ---")
    
    # Define path patterns for CMIP data files
    model = config.CMIP_CONFIG["models"][0]  # Use first model
    scenarios = config.CMIP_CONFIG["scenarios"]
    variables = config.CMIP_CONFIG["variables"]
    
    # Process CMIP data - require actual data files
    cmip_datasets = []
    found_data = False
    
    for scenario in scenarios:
        for variable in variables:
            # Direct path to an expected file
            file_name = f"macav2metdata_{variable}_{model}_r6i1p1_{scenario}_{config.CMIP_CONFIG['years']}_{config.CMIP_CONFIG['region']}_{config.CMIP_CONFIG['frequency']}.nc"
            file_path = os.path.join(config.CMIP_CONFIG["data_dir"], file_name)
            
            if os.path.exists(file_path):
                found_data = True
                print(f"Processing CMIP data file: {file_path}")
                
                try:
                    # Try loading with standard processor
                    processor = CMIPProcessor(file_path)
                except ValueError as e:
                    if "calendar" in str(e):
                        print(f"Warning: Calendar issue detected. Loading with decode_times=False")
                        import xarray as xr
                        dataset = xr.open_dataset(file_path, decode_times=False)
                        processor = CMIPProcessor(file_path)
                        processor.dataset = dataset
                    else:
                        raise
                
                try:
                    # Process to datacube format
                    dataset = processor.process_to_datacube(
                        lat_bucket_size=resolution,
                        lon_bucket_size=resolution,
                        time_bucket_size=temporal_resolution,
                        spatial_agg_method=CMIPAggregation.MEAN,
                        temporal_agg_method=CMIPAggregation.MEAN
                    )
                    cmip_datasets.append(dataset)
                except Exception as e:
                    print(f"Error processing {file_path}: {e}")
                    print("Trying simplified approach...")
                    
                    # Use a simple approach with striding
                    lat_stride = 10  # Simple stride values as fallback
                    lon_stride = 10
                    time_stride = 3 if temporal_resolution == "3ME" else 1
                    
                    simplified = processor.dataset.isel(
                        lat=slice(0, None, lat_stride),
                        lon=slice(0, None, lon_stride),
                        time=slice(0, None, time_stride)
                    )
                    
                    cmip_datasets.append(simplified)
    
    # Fail if no data files were found
    if not found_data:
        var = config.CMIP_CONFIG["variables"][0]
        scenario = config.CMIP_CONFIG["scenarios"][0]
        file_name = f"macav2metdata_{var}_{model}_r6i1p1_{scenario}_{config.CMIP_CONFIG['years']}_{config.CMIP_CONFIG['region']}_{config.CMIP_CONFIG['frequency']}.nc"
        file_path = os.path.join(config.CMIP_CONFIG["data_dir"], file_name)
        raise FileNotFoundError(f"No CMIP data files found. Expected file: {file_path}")
    
    if not cmip_datasets:
        raise RuntimeError("Failed to process any CMIP datasets")
    
    # Return the first dataset for now
    # In a real implementation, you would combine multiple scenarios
    print(f"CMIP processing complete. Output shape: {cmip_datasets[0].dims}")
    return cmip_datasets[0]

def build_combined_datacube(landfire_data, cmip_data, output_path, resolution, temporal_resolution):
    """
    Build a unified datacube combining vegetation and climate data.
    
    Args:
        landfire_data: Processed LANDFIRE dataset
        cmip_data: Processed CMIP dataset
        output_path: Path to save the combined datacube
        resolution: Spatial resolution in degrees
        temporal_resolution: Temporal resolution
    """
    print(f"\n--- Building Combined Datacube ---")
    
    # Initialize the datacube builder
    builder = DatacubeBuilder()
    
    # Add datasets
    builder.add_dataset("vegetation", landfire_data)
    builder.add_dataset("climate", cmip_data)
    
    # Build a unified datacube
    print(f"Building unified datacube with resolution {resolution}°...")
    unified_cube = builder.build_datacube(
        lat_resolution=resolution,
        lon_resolution=resolution,
        time_resolution=temporal_resolution,
        interpolation_method=InterpolationMethod.NEAREST  # Better for categorical data
    )
    
    print(f"Combined datacube dimensions: {unified_cube.dims}")
    print(f"Variables: {list(unified_cube.data_vars)}")
    
    # Create the output directory if it doesn't exist
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Save the combined datacube
    print(f"Saving combined datacube to {output_path}...")
    builder.save_datacube(output_path)
    
    print("Datacube building complete!")
    return unified_cube

def main():
    """Main function to build the Black Hills datacube."""
    args = parse_arguments()
    
    print("=" * 80)
    print("Black Hills Datacube Builder")
    print("=" * 80)
    print(f"Region: {config.BLACK_HILLS_BBOX_WGS84['name']}")
    print(f"Bounding Box: {config.BLACK_HILLS_BBOX_STRING}")
    print(f"Output Path: {args.output}")
    print(f"Spatial Resolution: {args.resolution}°")
    print(f"Temporal Resolution: {args.temp_resolution}")
    print("=" * 80)
    
    try:
        # Process LANDFIRE data
        landfire_data = process_landfire_data(args.resolution)
        
        # Process CMIP data
        cmip_data = process_cmip_data(args.resolution, args.temp_resolution)
        
        # Build combined datacube
        unified_cube = build_combined_datacube(
            landfire_data, 
            cmip_data, 
            args.output,
            args.resolution,
            args.temp_resolution
        )
        
        print("\nBlack Hills Datacube successfully created!")
        print(f"Output file: {args.output}")
        print(f"Datacube dimensions: {unified_cube.dims}")
        print(f"Variables: {list(unified_cube.data_vars)}")
        
    except Exception as e:
        print("\n" + "!" * 80)
        print(f"ERROR: Failed to create datacube: {str(e)}")
        print("!" * 80)
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()