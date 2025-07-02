#!/usr/bin/env python
"""
Test suite for the LANDFIRE processor module.

This module contains unit tests for the LandfireProcessor class
to ensure correct functionality for downloading, processing, and
bucketing LANDFIRE vegetation data.
"""

import os
import unittest
import tempfile
import numpy as np
import xarray as xr
from unittest.mock import patch, MagicMock

from landfire_processor import LandfireProcessor, AggregationMethod

class TestLandfireProcessor(unittest.TestCase):
    """Test cases for the LandfireProcessor class."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        # Create a temporary directory for test data
        self.temp_dir = tempfile.TemporaryDirectory()
        
        # Create a small test bounding box in Montana
        self.test_bbox = "-107.70 46.56 -106.02 47.34"
        
        # Initialize the processor with mocked landfire client
        with patch('landfire.Landfire') as mock_landfire:
            self.processor = LandfireProcessor(
                bbox=self.test_bbox,
                data_dir=self.temp_dir.name
            )
            # Replace the actual client with the mock
            self.processor.lf_client = mock_landfire
    
    def tearDown(self):
        """Clean up after each test method."""
        # Close the temporary directory
        self.temp_dir.cleanup()
    
    def test_initialization(self):
        """Test that processor initializes correctly."""
        # Check that the bounding box was parsed correctly
        self.assertEqual(self.processor.minx, -107.70)
        self.assertEqual(self.processor.miny, 46.56)
        self.assertEqual(self.processor.maxx, -106.02)
        self.assertEqual(self.processor.maxy, 47.34)
        
        # Check that data_dir is set correctly
        self.assertEqual(self.processor.data_dir, self.temp_dir.name)
    
    def test_download_data(self):
        """Test downloading LANDFIRE data."""
        # Replace the actual client with a mock
        self.processor.lf_client = MagicMock()
        self.processor.lf_client.request_data.return_value = None
        
        # Call download_data
        output_path = self.processor.download_data("220EVT")
        
        # Check that output path is set correctly
        expected_path = os.path.join(self.temp_dir.name, "landfire_220EVT.zip")
        self.assertEqual(output_path, expected_path)
        self.assertEqual(self.processor.raw_data_path, expected_path)
    
    @patch('zipfile.ZipFile')
    def test_extract_data(self, mock_zipfile):
        """Test extracting downloaded data."""
        # Set up the mock zipfile
        mock_zip_instance = MagicMock()
        mock_zipfile.return_value.__enter__.return_value = mock_zip_instance
        
        # Set up listdir mock to return a fake TIFF file
        with patch('os.listdir', return_value=['test_data.tif']):
            # Set raw_data_path
            self.processor.raw_data_path = os.path.join(self.temp_dir.name, "landfire_220EVT.zip")
            
            # Call extract_data
            output_dir = self.processor.extract_data()
            
            # Check that zipfile was extracted to the correct location
            mock_zip_instance.extractall.assert_called_once()
            
            # Check that output directory is correct
            expected_dir = os.path.join(self.temp_dir.name, "extracted")
            self.assertEqual(output_dir, expected_dir)
            
            # Check that tiff_path was set correctly
            expected_tiff = os.path.join(expected_dir, "test_data.tif")
            self.assertEqual(self.processor.tiff_path, expected_tiff)
    
    @patch('rasterio.open')
    def test_create_dataset(self, mock_rasterio_open):
        """Test creating xarray dataset from TIFF."""
        # Create mock rasterio dataset
        mock_src = MagicMock()
        mock_src.read.return_value = np.ones((100, 100), dtype=np.int32)
        mock_src.transform = MagicMock()
        mock_src.transform.a = 0.01
        mock_src.transform.b = 0
        mock_src.transform.c = -107.70
        mock_src.transform.d = 0
        mock_src.transform.e = -0.01
        mock_src.transform.f = 47.34
        mock_src.crs = "EPSG:4326"
        mock_src.nodata = -9999
        mock_src.shape = (100, 100)
        
        # Set up mock rasterio to return our mock source
        mock_rasterio_open.return_value.__enter__.return_value = mock_src
        
        # Set tiff_path
        self.processor.tiff_path = os.path.join(self.temp_dir.name, "extracted", "test_data.tif")
        
        # Call create_dataset
        dataset = self.processor.create_dataset()
        
        # Check that dataset was created successfully
        self.assertIsInstance(dataset, xr.Dataset)
        self.assertIn("evt", dataset.data_vars)
        
        # Check that dataset was stored in the processor
        self.assertEqual(dataset, self.processor.raw_dataset)
    
    def test_reproject_to_latlon(self):
        """Test reprojecting dataset to lat/lon coordinates."""
        # Create a fake raw dataset
        y = np.arange(100)
        x = np.arange(100)
        data = np.ones((100, 100), dtype=np.int32)
        
        self.processor.raw_dataset = xr.Dataset(
            data_vars={"evt": (["y", "x"], data)},
            coords={"y": y, "x": x},
            attrs={"crs": "EPSG:4326"}
        )
        
        # Call reproject_to_latlon
        result = self.processor.reproject_to_latlon()
        
        # Check that result dataset has correct dimensions
        self.assertIsInstance(result, xr.Dataset)
        self.assertIn("evt", result.data_vars)
        self.assertIn("lat", result.coords)
        self.assertIn("lon", result.coords)
        
        # Check that dataset was stored in processor
        self.assertEqual(result, self.processor.processed_dataset)
    
    def test_bucket_spatial(self):
        """Test spatial bucketing of LANDFIRE data."""
        # Create a fake processed dataset with lat/lon coords
        lat = np.linspace(46.56, 47.34, 10)
        lon = np.linspace(-107.70, -106.02, 10)
        data = np.ones((10, 10), dtype=np.int32)
        
        self.processor.processed_dataset = xr.Dataset(
            data_vars={"evt": (["lat", "lon"], data)},
            coords={"lat": lat, "lon": lon}
        )
        
        # Call bucket_spatial
        result = self.processor.bucket_spatial(
            lat_bucket_size=0.2,
            lon_bucket_size=0.2,
            agg_method=AggregationMethod.MODE
        )
        
        # Check that result has correct structure
        self.assertIsInstance(result, xr.Dataset)
        self.assertIn("evt", result.data_vars)
        self.assertIn("lat_bins", result.coords)
        self.assertIn("lon_bins", result.coords)
        
        # TEST DIFFERENT AGGREGATION METHODS
        for agg_method in [
            AggregationMethod.MAJORITY,
            AggregationMethod.FIRST,
            AggregationMethod.LAST
        ]:
            result = self.processor.bucket_spatial(
                lat_bucket_size=0.2,
                lon_bucket_size=0.2,
                agg_method=agg_method
            )
            self.assertIsInstance(result, xr.Dataset)
            self.assertIn("evt", result.data_vars)
    
    @patch('xarray.Dataset.to_netcdf')
    def test_save_dataset(self, mock_to_netcdf):
        """Test saving dataset to NetCDF file."""
        # Create a simple dataset
        ds = xr.Dataset(
            data_vars={"evt": (["lat", "lon"], np.ones((10, 10)))},
            coords={
                "lat": np.linspace(46.56, 47.34, 10),
                "lon": np.linspace(-107.70, -106.02, 10)
            }
        )
        
        # Call save_dataset
        output_path = os.path.join(self.temp_dir.name, "test_output.nc")
        self.processor.save_dataset(ds, output_path)
        
        # Check that to_netcdf was called with correct path
        mock_to_netcdf.assert_called_once_with(output_path)

if __name__ == "__main__":
    unittest.main()