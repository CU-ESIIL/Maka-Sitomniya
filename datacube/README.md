# Maka-Sitomniya DataCube

A flexible framework for creating, manipulating, and analyzing multi-dimensional environmental data cubes with a focus on Indigenous data sovereignty.

## Overview

This datacube implementation provides tools for processing climate and environmental data into standardized, analysis-ready datacubes. It is designed to:

- Handle various data sources (starting with CMIP climate data)
- Provide flexible spatial and temporal aggregation
- Support multiple aggregation methods (mean, median, max, min, etc.)
- Enable combining multiple datasets into unified datacubes
- Facilitate data exploration and analysis through Jupyter notebooks

## Directory Structure

```
datacube/
├── data/               # Raw and processed data files
├── notebooks/          # Jupyter notebooks for exploration and analysis
├── scripts/            # Processing scripts and core implementation
│   ├── cmip_processor.py       # CMIP data processing utilities
│   ├── datacube_builder.py     # Tools for combining datasets
│   └── test_cmip_processor.py  # Unit tests
└── environment.yml     # Conda environment specification
```

## Regional Focus: Black Hills

This implementation includes specific support for the Black Hills region in South Dakota, with predefined bounding boxes and configuration settings.

**Black Hills Region (WGS84 coordinates):**
- North: 44.652° latitude
- South: 43.480° latitude
- West: -104.705° longitude
- East: -103.264° longitude

A dedicated script for generating Black Hills datacubes is provided in `scripts/blackhills_datacube.py`.

## Current Capabilities

### CMIP Processor

The `CMIPProcessor` class provides functionality to:

- Load CMIP climate data from NetCDF files
- Determine native spatial and temporal resolutions
- Apply spatial bucketing with custom resolutions
- Apply temporal bucketing with custom time periods
- Create standardized datacubes with multiple aggregation methods
- Save processed datacubes to NetCDF format

### LANDFIRE Processor

The `LandfireProcessor` class provides functionality to:

- Download LANDFIRE Existing Vegetation Type (EVT) data for specific regions
- Extract data from ZIP archives to GeoTIFF format
- Convert categorical vegetation data to xarray Datasets
- Reproject data to standard latitude/longitude coordinates
- Apply spatial bucketing with MODE aggregation (most common value)
- Save processed categorical data to NetCDF format

### DataCube Builder

The `DatacubeBuilder` class allows:

- Loading multiple datasets (including CMIP and LANDFIRE data)
- Aligning datasets to a common grid and time scale
- Combining multiple variables into a unified datacube
- Handling different interpolation methods for alignment
- Saving combined datacubes for further analysis

## Example Usage

```python
# Example 1: Load and process CMIP climate data
from scripts.cmip_processor import CMIPProcessor, AggregationMethod

# Initialize processor with CMIP data file
processor = CMIPProcessor("data/macav2metdata_huss_CCSM4_r6i1p1_rcp45_2021_2025_CONUS_monthly.nc")

# Create a datacube with 0.5-degree spatial resolution and quarterly temporal aggregation
datacube = processor.process_to_datacube(
    lat_bucket_size=0.5,
    lon_bucket_size=0.5,
    time_bucket_size='3ME',  # 3-month/quarterly
    spatial_agg_method=AggregationMethod.MEAN,
    temporal_agg_method=AggregationMethod.MEAN
)

# Save the processed datacube
processor.save_datacube(datacube, "data/processed_cmip_datacube.nc")
```

```python
# Example 2: Download and process LANDFIRE vegetation data
from scripts.landfire_processor import LandfireProcessor, AggregationMethod

# Define area of interest in South Dakota (minx miny maxx maxy)
bbox = "-103.50 43.00 -102.00 44.00"

# Initialize the LANDFIRE processor
processor = LandfireProcessor(bbox=bbox, data_dir="data/landfire")

# Download Existing Vegetation Type data (2020 version)
processor.download_data("220EVT")

# Extract and load the data
processor.extract_data()
dataset = processor.create_dataset()

# Reproject to latitude/longitude coordinates
reprojected = processor.reproject_to_latlon()

# Apply spatial bucketing with MODE aggregation (most common value)
bucketed = processor.bucket_spatial(
    lat_bucket_size=0.01,
    lon_bucket_size=0.01,
    agg_method=AggregationMethod.MODE
)

# Save the processed vegetation data
processor.save_dataset(bucketed, "data/processed_landfire_evt.nc")
```

```python
# Example 3: Combine climate and vegetation data into a unified datacube
from scripts.datacube_builder import DatacubeBuilder, InterpolationMethod

# Initialize datacube builder
builder = DatacubeBuilder()

# Add datasets
builder.add_dataset("climate", cmip_datacube)
builder.add_dataset("vegetation", landfire_datacube)

# Build unified datacube
unified_datacube = builder.build_datacube(
    lat_resolution=0.1,
    lon_resolution=0.1,
    time_resolution='1ME',  # Monthly
    interpolation_method=InterpolationMethod.NEAREST
)

# Save the combined datacube
builder.save_datacube("data/unified_datacube.nc")
```

```python
# Example 4: Create a complete Black Hills region datacube
from scripts.blackhills_datacube import process_landfire_data, process_cmip_data, build_combined_datacube

# Process vegetation data for Black Hills
landfire_data = process_landfire_data(resolution=0.01)  # ~1km resolution

# Process climate data for Black Hills
cmip_data = process_cmip_data(resolution=0.01, temporal_resolution='ME')  # Monthly

# Build combined datacube
unified_cube = build_combined_datacube(
    landfire_data,
    cmip_data,
    output_path="data/blackhills_datacube.nc",
    resolution=0.01,
    temporal_resolution='ME'
)

# Alternatively, use the command line:
# python scripts/blackhills_datacube.py --output data/blackhills_datacube.nc --resolution 0.01
```

## Development Roadmap

### Completed
- ✅ Basic directory structure setup
- ✅ CMIP data processor implementation
- ✅ LANDFIRE vegetation data processor implementation
- ✅ Support for flexible spatial bucketing
- ✅ Support for flexible temporal bucketing
- ✅ Support for categorical data with MODE aggregation
- ✅ Multiple aggregation methods
- ✅ Unit tests for core functionality
- ✅ Datacube builder for combining datasets
- ✅ Notebook for exploring CMIP data
- ✅ Notebook for exploring LANDFIRE vegetation data
- ✅ Notebook for exploring combined datacubes

### In Progress
- 🔄 Processing real-world CMIP datasets
- 🔄 Enhancing documentation and examples
- 🔄 Implementing visualization utilities
- 🔄 Improving test coverage

### To Do
- 📋 Add support for additional data sources (e.g., satellite imagery, weather station data)
- 📋 Implement data validation and quality checks
- 📋 Add geospatial operations (e.g., clipping to specific regions, reprojection)
- 📋 Create resampling utilities for different spatial references
- 📋 Develop tools for statistical analysis across dimensions
- 📋 Add support for masking by region or administrative boundaries
- 📋 Implement metadata management and provenance tracking
- 📋 Create tools for time series analysis
- 📋 Add data export functionality for various formats
- 📋 Develop web visualization components
- 📋 Integration with other Earth data science frameworks
- 📋 Create user-friendly command-line interface
- 📋 Add support for distributed processing for large datasets

## Getting Started

### Environment Setup

```bash
# Create the conda environment
conda env create -f environment.yml

# Activate the environment
conda activate datacube
```

### Running the Tests

```bash
# Run all tests
python -m pytest scripts/

# Run with verbose output
python -m pytest -xvs scripts/
```

### Exploring with Notebooks

Start with the following notebooks:
1. `notebooks/cmip_data_exploration.ipynb` - Explore individual CMIP datasets
2. `notebooks/datacube_exploration.ipynb` - Explore combined datasets in a unified datacube

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

When contributing:
1. Make sure all tests pass
2. Add tests for new functionality
3. Update documentation as needed
4. Follow existing code style

## License

This project is part of the Maka-Sitomniya initiative. See the main repository for license information.