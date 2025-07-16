# Maka Sitomniya DataCube

A comprehensive climate and environmental data analysis framework designed specifically for the Black Hills region, providing tools for data acquisition, processing, analysis, and visualization of multi-source environmental datasets.

## Overview

The Maka Sitomniya DataCube is a modular Python framework that enables Tribal communities and researchers to access, process, and analyze environmental data for vulnerability assessments, mitigation planning, and adaptation strategies. This framework integrates climate projections, land cover data, and geospatial features to support informed decision-making and strengthen environmental sovereignty.

## Repository Structure

```
datacube/
├── README.md                           # This file
├── config.py                           # Configuration and region definitions
├── environment.yml                     # Conda environment specification
├── data/                              # Data directory (see Data Management below)
│   └── data_download_note.txt         # Data hosting information
├── notebooks/                         # Jupyter analysis notebooks
│   ├── burned_area_exploration.ipynb  # Fire history analysis
│   ├── dynamic_world_exploration.ipynb # Land cover classification
│   ├── global_forest_change.ipynb     # Forest change detection
│   ├── landfire_exploration.ipynb     # LANDFIRE vegetation analysis
│   ├── maca_data_exploration.ipynb    # Climate data analysis
│   ├── NLCD.ipynb                     # National Land Cover Database
│   └── surface_water_exploration.ipynb # Water body mapping
|   └── nrcs_soil_exploration.ipynb    # NRCS soil exploration
├── scripts/                           # Data collection and processing scripts
│   ├── find_mines.py                  # Mining feature extraction
│   ├── gee_dynamic_world.js          # Google Earth Engine land cover
│   ├── gee_fires.js                  # Google Earth Engine fire detection
│   ├── gee_surface_water.js          # Google Earth Engine surface water
│   ├── maca_seasonal_batch.py        # MACA climate data downloader
│   ├── osm_data_gatherer.py          # OpenStreetMap data collection
│   └── osm_to_geojson.py             # OSM to GeoJSON conversion
├── landcover_percentage_analysis.py   # Land cover correlation analysis
├── landcover_percentage_correlations.csv # Analysis results
├── landcover_percentage_scatter_plots.png # Visualizations
└── landcover_correlation_summary.png  # Summary plots
```

## Data Management

### Data Directory Structure
The `data/` directory contains large environmental datasets that are **not stored in Git** due to size constraints. Only `data_download_note.txt` is tracked in version control.

**Data is hosted externally** on CyVerse (link to be provided) and should be downloaded locally for analysis.

Expected data structure when downloaded:
```
data/
├── data_download_note.txt             # [TRACKED] Data hosting info
├── maca/                              # [IGNORED] MACA climate data
│   ├── MACA_Seasonal-historical-*/    # Historical climate scenarios
│   └── MACA_Seasonal-rcp45-*/        # Future climate projections
├── EarthEngine_BurnedArea/            # [IGNORED] Annual burned area rasters
├── EarthEngine_SurfaceWater/          # [IGNORED] Surface water extent
├── landfire/                          # [IGNORED] LANDFIRE vegetation data
├── osm/                              # [IGNORED] OpenStreetMap features
└── DW_BlackHills_mode.tif            # [IGNORED] Dynamic World land cover
```

### Data Download
1. **Access CyVerse data repository**: [Link to be provided]
2. **Download required datasets** to the `data/` directory
3. **Maintain directory structure** as shown above

## Core Components

### 1. Configuration (`config.py`)
- **Regional definitions**: Black Hills bounding box in multiple projections
- **Data paths**: Standardized directory structure

### 2. Data Collection Scripts (`scripts/`)

#### Climate Data Collection
- **`maca_seasonal_batch.py`**: Earth Engine seasonal downloader
  - Creates seasonal composites from MACA v2 data
  - **Features**: Progress tracking, throttling, dry-run mode
  - **Output**: GeoTIFF files organized by scenario/model/variable
  - **Dependencies**: earthengine-api

#### OpenStreetMap Integration
- **`osm_data_gatherer.py`**: OSM feature extraction
  - Collects roads, buildings, landuse, natural features, amenities
  - **API**: Overpass API for Black Hills region
  - **Output**: JSON files organized by feature type

- **`find_mines.py`**: Mining feature identification
  - Extracts mining-related features from OSM data
  - **Methods**: Keyword matching and tag analysis
  - **Output**: GeoJSON with mining locations and classifications

- **`osm_to_geojson.py`**: OSM to GeoJSON conversion utility

#### Google Earth Engine Scripts
- **`gee_dynamic_world.js`**: Land cover classification
  - Creates Dynamic World land cover composites
  - **Output**: Mode composite rasters for Black Hills

- **`gee_surface_water.js`**: Surface water extent mapping
- **`gee_fires.js`**: Fire and burned area detection

### 3. Analysis Notebooks (`notebooks/`)

#### Climate Analysis
- **`maca_data_exploration.ipynb`**: Comprehensive climate analysis
  - Time series analysis with trend detection
  - Seasonal distribution analysis and climate velocity
  - **Features**: Interactive Plotly visualizations, multiple scenario comparison

#### Land Cover Analysis
- **`dynamic_world_exploration.ipynb`**: Land cover classification
  - Spatial distribution and landscape composition analysis
  - Forest fragmentation assessment and Shannon diversity
  - **Features**: Statistical analysis, visualization of land cover patterns

- **`NLCD.ipynb`**: National Land Cover Database analysis
- **`nrcs_soil_exploration.ipynb`**: Natural Resources Conservation Service

#### Environmental Integration
- **`landfire_exploration.ipynb`**: LANDFIRE vegetation analysis
- **`burned_area_exploration.ipynb`**: Fire history analysis
- **`surface_water_exploration.ipynb`**: Water body mapping
- **`global_forest_change.ipynb`**: Forest change detection

### 4. Correlation Analysis Scripts

#### Land Cover-Climate Relationships
- **`landcover_percentage_analysis.py`**: Comprehensive correlation analysis
  - Calculates land cover percentages within climate pixels
  - **Features**: Scatter plots, correlation matrices, statistical significance
  - **Output**: Correlation CSVs, visualization PNGs

## Data Sources

### Climate Data
- **MACA v2**: Downscaled climate projections (4 km resolution)
  - **Temporal Coverage**: 1950-2099
  - **Variables**: Temperature (min/max), Precipitation
  - **Models**: GFDL-ESM2M and others
  - **Scenarios**: Historical, RCP 4.5

### Geospatial Data
- **Google Earth Engine**: 
  - Dynamic World land cover (10 m resolution)
  - Surface water extent (30 m resolution)
  - Burned area mapping (500 m resolution)
- **OpenStreetMap**: Infrastructure and geographic features
- **LANDFIRE**: Vegetation and fuel data for fire analysis
- **NLCD**: National Land Cover Database
- **NRCS**: Natural Resources Conservation Service

## Key Features

## Installation

### Prerequisites
- Python 3.8+
- Conda or pip package manager
- Earth Engine account (for GEE scripts)

### Setup
1. **Clone the repository**
   ```bash
   git clone https://github.com/CU-ESIIL/Maka-Sitomniya.git
   cd Maka-Sitomniya/datacube
   ```

2. **Create conda environment**
   ```bash
   conda env create -f environment.yml
   conda activate maka-sitomniya
   ```

3. **Install additional dependencies (if needed)**
   ```bash
   pip install -r osm_requirements.txt
   ```

4. **Set up Earth Engine authentication**
   ```bash
   earthengine authenticate
   ```

5. **Download data from CyVerse**
   - Access the CyVerse data repository (link to be provided)
   - Download datasets to the `data/` directory
   - Maintain the expected directory structure

## Quick Start

### 1. Data Collection
```bash
# Download MACA climate data
python scripts/maca_seasonal_batch.py

# Collect OpenStreetMap data
python scripts/osm_data_gatherer.py

# Extract mining features
python scripts/find_mines.py
```

### 2. Data Analysis
```python
# Load configuration
import config

# Access Black Hills bounding box
bbox = config.BLACK_HILLS_BBOX_WGS84
print(f"Region: {bbox['name']}")
print(f"Bounds: {config.BLACK_HILLS_BBOX_STRING}")

# Run correlation analysis
python landcover_percentage_analysis.py
```

### 3. Interactive Analysis
```bash
# Launch Jupyter and explore notebooks
jupyter notebook notebooks/
```

## Example Workflows

### Climate Analysis Workflow
1. **Data Download**: Use `maca_seasonal_batch.py` to download seasonal climate data
2. **Analysis**: Use `maca_data_exploration.ipynb` for trend analysis
3. **Visualization**: Generate maps and time series plots

### Land Cover Analysis Workflow
1. **Data Collection**: Run `gee_dynamic_world.js` to extract land cover data
2. **Correlation Analysis**: Use `landcover_percentage_analysis.py` 
3. **Visualization**: Generate scatter plots and correlation matrices
4. **Integration**: Combine with climate data for environmental analysis

### Environmental Integration Workflow
1. **Multi-source Data**: Combine MACA, Dynamic World, and OSM data
2. **Spatial Analysis**: Perform correlation analysis across data sources
3. **Temporal Analysis**: Analyze trends and seasonal patterns
4. **Reporting**: Generate comprehensive analysis reports

## Configuration

The `config.py` file contains key configuration settings:

### Regional Definitions
```python
# Black Hills bounding box (WGS84)
BLACK_HILLS_BBOX_WGS84 = {
    "north": 44.652,
    "south": 43.480,
    "west": -104.705,
    "east": -103.264,
    "projection": "EPSG:4326"
}
```

### Data Paths
```python
# Default data directories
DATA_DIR = "data/"
OUTPUTS_DIR = "data/processed/"
```

### Processing Parameters
```python
# Default settings
DEFAULT_SPATIAL_RESOLUTION = 30  # meters
DEFAULT_TEMPORAL_RESOLUTION = "ME"  # Month end
DEFAULT_CRS = "EPSG:4326"  # WGS84
```

## Contributing

We welcome contributions from the community! Please see our [Contributing Guidelines](../docs/contributing.md) for details on:
- Code style and conventions
- Pull request process
- Issue reporting
- Development setup

## License

This project is licensed under the terms specified in the [LICENSE](../LICENSE) file.

## Support

For questions, issues, or contributions:
- **GitHub Issues**: [Report bugs or request features](https://github.com/CU-ESIIL/Maka-Sitomniya/issues)
- **Documentation**: [GitHub Pages](https://cu-esiil.github.io/Maka-Sitomniya/)
- **Email**: Contact the technical lead or project PIs

## Acknowledgments

This work is supported by:
- Environmental Data Science Innovation and Impact Lab (ESIIL)
- National Science Foundation
- University of Colorado Boulder
- Tribal partners and communities

## Citation

If you use this framework in your research, please cite:

```bibtex
@software{maka_sitomniya_datacube,
  title={Maka Sitomniya DataCube: Climate and Environmental Data Analysis Framework},
  author={Two Eagle, Phil and Yellow Thunder, Elisha Wakinyan Zi and Jones-Sanovia, Lilly and others},
  year={2024},
  publisher={Environmental Data Science Innovation and Impact Lab},
  url={https://github.com/CU-ESIIL/Maka-Sitomniya}
}
```
