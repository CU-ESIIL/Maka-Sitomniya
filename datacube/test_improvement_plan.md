# Test Improvement Plan

Based on the coverage report, this document outlines specific test improvements to increase coverage and enhance reliability of the datacube implementation.

## Additional Tests for CMIPProcessor

### 1. Combined Spatial and Temporal Bucketing Test

```python
def test_combined_spatial_temporal_bucketing(self):
    """Test combined spatial and temporal bucketing."""
    # Process with both spatial and temporal bucketing
    datacube = self.processor.process_to_datacube(
        lat_bucket_size=2.5,
        lon_bucket_size=2.5,
        time_bucket_size='3ME',
        spatial_agg_method=AggregationMethod.MEAN,
        temporal_agg_method=AggregationMethod.MEAN
    )
    
    # Verify the result has both spatial and temporal bucketing applied
    self.assertIn('lat_bins', datacube.coords)
    self.assertIn('lon_bins', datacube.coords)
    self.assertIn('time', datacube.dims)
    
    # Verify dimensions reduced as expected
    self.assertLess(len(datacube.time), len(self.processor.dataset.time))
    
    # Test different combinations of aggregation methods
    for spatial_method in [AggregationMethod.MEAN, AggregationMethod.MAX]:
        for temporal_method in [AggregationMethod.MEAN, AggregationMethod.MIN]:
            combined = self.processor.process_to_datacube(
                lat_bucket_size=2.5,
                lon_bucket_size=2.5,
                time_bucket_size='3ME',
                spatial_agg_method=spatial_method,
                temporal_agg_method=temporal_method
            )
            self.assertIn('lat_bins', combined.coords)
            self.assertIn('lon_bins', combined.coords)
            self.assertIn('time', combined.dims)
```

### 2. Error Handling Tests

```python
def test_error_handling(self):
    """Test error handling for invalid inputs."""
    # Invalid file path
    with self.assertRaises(FileNotFoundError):
        invalid_processor = CMIPProcessor("nonexistent_file.nc")
    
    # Invalid aggregation method
    with self.assertRaises(ValueError):
        self.processor.bucket_spatial(
            lat_bucket_size=1.0,
            lon_bucket_size=1.0,
            agg_method="invalid_method"  # Not an AggregationMethod
        )
    
    # Test saving to invalid path
    with tempfile.TemporaryDirectory() as invalid_dir:
        invalid_path = os.path.join(invalid_dir, "subfolder/invalid.nc")
        with self.assertRaises(Exception):  # Should fail because subfolder doesn't exist
            self.processor.save_datacube(self.processor.dataset, invalid_path)
```

### 3. Edge Case Tests

```python
def test_small_dataset_handling(self):
    """Test handling of small datasets with few points."""
    # Create a minimal dataset with just 2x2 grid and 2 time points
    lats = np.array([40, 41])
    lons = np.array([-105, -104])
    times = np.array([np.datetime64('2021-01-01'), np.datetime64('2021-02-01')])
    
    # Create simple data
    temp_data = np.random.rand(2, 2, 2) * 30
    
    # Create synthetic dataset
    small_dataset = xr.Dataset(
        data_vars={
            'temperature': (['time', 'lat', 'lon'], temp_data)
        },
        coords={
            'lon': ('lon', lons),
            'lat': ('lat', lats),
            'time': ('time', times)
        }
    )
    
    # Save to a temporary file
    with tempfile.NamedTemporaryFile(suffix='.nc') as tmp:
        small_dataset.to_netcdf(tmp.name)
        
        # Initialize processor with small dataset
        small_processor = CMIPProcessor(tmp.name)
        
        # Test spatial bucketing (should maintain the data since it's already small)
        bucket_size = 2.0  # Larger than the grid spacing
        bucketed = small_processor.bucket_spatial(bucket_size, bucket_size)
        
        # Should still have valid data
        self.assertTrue(len(bucketed.data_vars) > 0)
        
        # Test temporal bucketing
        time_bucketed = small_processor.bucket_temporal('2ME')  # Larger than time range
        
        # Should have reduced to 1 time point
        self.assertEqual(len(time_bucketed.time), 1)
```

## Additional Tests for DatacubeBuilder

### 1. Regridding Tests

```python
def test_regridding_methods(self):
    """Test different regridding methods."""
    # Add datasets with different grids
    self.builder.add_dataset("temperature", self.dataset1)
    self.builder.add_dataset("precipitation", self.dataset2)
    
    # Test each interpolation method
    for method in [
        InterpolationMethod.NEAREST,
        InterpolationMethod.LINEAR,
        InterpolationMethod.CUBIC,
        InterpolationMethod.BILINEAR
    ]:
        unified_cube = self.builder.build_datacube(
            lat_resolution=1.0,
            lon_resolution=1.0,
            time_resolution='1ME',
            interpolation_method=method
        )
        
        # Verify the result has common grid
        self.assertIn("temperature_temperature", unified_cube.data_vars)
        self.assertIn("precipitation_precipitation", unified_cube.data_vars)
        
        # Check for NaN values in the result
        temp_var = unified_cube["temperature_temperature"]
        precip_var = unified_cube["precipitation_precipitation"]
        
        # Calculate percentage of valid (non-NaN) values
        temp_valid = np.count_nonzero(~np.isnan(temp_var.values)) / temp_var.size
        precip_valid = np.count_nonzero(~np.isnan(precip_var.values)) / precip_var.size
        
        # Each method should preserve a good portion of the data
        print(f"Method {method.value} - Valid temperature: {temp_valid:.2%}, Valid precipitation: {precip_valid:.2%}")
        self.assertGreater(temp_valid, 0.7, f"Too many NaN values with {method.value}")
        self.assertGreater(precip_valid, 0.7, f"Too many NaN values with {method.value}")
```

### 2. Fill Value Tests

```python
def test_fill_values(self):
    """Test handling of fill values."""
    # Add datasets
    self.builder.add_dataset("temperature", self.dataset1)
    self.builder.add_dataset("precipitation", self.dataset2)
    
    # Build datacube with fill value
    fill_value = -9999.0
    unified_cube = self.builder.build_datacube(
        lat_resolution=1.0,
        lon_resolution=1.0,
        time_resolution='1ME',
        interpolation_method=InterpolationMethod.LINEAR,
        fill_value=fill_value
    )
    
    # Verify fill values are used
    temp_var = unified_cube["temperature_temperature"]
    precip_var = unified_cube["precipitation_precipitation"]
    
    # Check if NaN values are replaced with fill value
    temp_has_fill = np.any(temp_var.values == fill_value)
    precip_has_fill = np.any(precip_var.values == fill_value)
    
    self.assertTrue(temp_has_fill or precip_has_fill or
                   (not np.any(np.isnan(temp_var.values)) and not np.any(np.isnan(precip_var.values))),
                   "Fill value not applied properly")
```

## Implementation Plan

1. Start by implementing the combined spatial and temporal bucketing test, as this covers the largest gap.
2. Add error handling tests to improve robustness.
3. Implement regridding tests to better cover the DatacubeBuilder.
4. Add edge case tests for small datasets and fill values.

These additions should significantly improve the test coverage and ensure the datacube implementation works correctly across a wide range of use cases.