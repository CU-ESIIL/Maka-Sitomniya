# Google Earth Engine Signup Guide

## 🚨 Current Status
You've successfully installed and authenticated with Google Earth Engine, but you need to register for access.

The error message indicates:
```
Not signed up for Earth Engine or project is not registered. 
Visit https://developers.google.com/earth-engine/guides/access
```

## ✅ What You've Already Done
1. ✅ Installed `earthengine-api` and `geemap`
2. ✅ Completed authentication with `earthengine authenticate`
3. ✅ Authentication token saved successfully

## 🔐 Next Step: Register for Earth Engine Access

### Option 1: Individual Account (Recommended)
1. **Visit**: https://earthengine.google.com/
2. **Click**: "Get Started" or "Sign Up"
3. **Choose**: "Register a Non-Commercial or Research Project"
4. **Fill out the form**:
   - Project name: "Climate Data Analysis" or similar
   - Project description: "Analyzing MACA v2 climate projections for research"
   - Intended use: Research/Academic
5. **Submit** and wait for approval (usually instant to 24 hours)

### Option 2: Google Cloud Project
1. **Visit**: https://console.cloud.google.com/
2. **Create** a new project or use existing one
3. **Enable** the Earth Engine API for your project
4. **Register** the project with Earth Engine

## 🧪 Test After Registration

Once you get approval, test with:

```python
import ee

# Initialize Earth Engine
ee.Initialize()

# Test MACA access
collection = ee.ImageCollection("IDAHO_EPSCOR/MACAv2_METDATA")
print(f"MACA collection size: {collection.size().getInfo()}")
```

## 📞 What to Do While Waiting

1. **Continue with the synthetic demo**: The `cmip_simple.ipynb` notebook works with demo data
2. **Explore the codebase**: Review the CMIP processing pipeline we built
3. **Read Earth Engine docs**: https://developers.google.com/earth-engine/

## 🎯 Once You Have Access

1. **Use our GEE fetcher**:
   ```python
   from cmip.download.gee_fetcher import download_black_hills_subset_gee
   
   # Download real MACA data
   file_path = download_black_hills_subset_gee(
       variable=Variable.TASMAX,
       model=ClimateModel.GFDL_ESM2M,
       scenario=Scenario.RCP45,
       year_start=2021,
       year_end=2025
   )
   ```

2. **Run the full pipeline** with real climate data
3. **Create visualizations** of actual climate projections

## 📚 Resources

- **Earth Engine Guide**: https://developers.google.com/earth-engine/guides/access
- **MACA Dataset**: https://developers.google.com/earth-engine/datasets/catalog/IDAHO_EPSCOR_MACAv2_METDATA
- **Earth Engine Python**: https://developers.google.com/earth-engine/guides/python_install

## ⏰ Timeline

- **Registration**: Submit form (5 minutes)
- **Approval**: Usually instant to 24 hours
- **Setup**: Test and start downloading data (5 minutes)

The infrastructure is ready - you just need Earth Engine access to get the real climate data!