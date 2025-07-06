/**
 * MACA v2 Seasonal Quick Start Script
 * 
 * Simplified version for immediate use - just copy and paste into 
 * Google Earth Engine Code Editor and click Run!
 * 
 * This downloads temperature and precipitation with seasonal preservation
 * for recent years as a starting point.
 */

// Your region (Black Hills) - modify coordinates for different areas
var region = ee.Geometry.Rectangle([-104.705, 43.480, -103.264, 44.652]);

// Quick configuration - modify these as needed
var QUICK_CONFIG = {
  variables: ['tasmax', 'pr'],  // Temperature and precipitation
  model: 'GFDL-ESM2M',          // Single model to start
  yearStart: 2015,              // Recent historical period
  yearEnd: 2023,                // Through recent years
  scenario: 'rcp45'             // Moderate emissions scenario
};

// Load MACA collection
var collection = ee.ImageCollection('IDAHO_EPSCOR/MACAv2_METDATA');

// Process one 3-year period with all seasons
function downloadPeriod(startYear) {
  var endYear = Math.min(startYear + 2, QUICK_CONFIG.yearEnd);
  
  // Define seasons
  var seasons = {
    'DJF_Winter': [12, 1, 2],
    'MAM_Spring': [3, 4, 5],
    'JJA_Summer': [6, 7, 8],
    'SON_Fall': [9, 10, 11]
  };
  
  // Process each variable
  QUICK_CONFIG.variables.forEach(function(variable) {
    
    // Process each season
    Object.keys(seasons).forEach(function(seasonName) {
      var months = seasons[seasonName];
      
      // Filter data
      var filtered = collection
        .filterDate(startYear + '-01-01', endYear + '-12-31')
        .filterBounds(region)
        .filter(ee.Filter.eq('model', QUICK_CONFIG.model))
        .filter(ee.Filter.eq('scenario', QUICK_CONFIG.scenario))
        .select(variable);
      
      // Filter by months
      var seasonalData = filtered.filter(
        ee.Filter.calendarRange(months[0], months[months.length-1], 'month')
      );
      
      // Calculate mean
      var mean = seasonalData.mean();
      
      // Create descriptive filename
      var filename = variable + '_' + startYear + '-' + endYear + '_' + seasonName;
      
      // Export
      Export.image.toDrive({
        image: mean,
        description: filename,
        folder: 'MACA_QuickStart',
        fileNamePrefix: filename,
        scale: 4000,
        region: region,
        maxPixels: 1e9
      });
      
      print('Started export: ' + filename);
    });
  });
}

// ============================================
// MAIN EXECUTION
// ============================================

print('🚀 MACA Seasonal Quick Start');
print('Region:', region);
print('Variables:', QUICK_CONFIG.variables);
print('Model:', QUICK_CONFIG.model);
print('Years:', QUICK_CONFIG.yearStart + '-' + QUICK_CONFIG.yearEnd);

// Process all 3-year periods
var totalExports = 0;
for (var year = QUICK_CONFIG.yearStart; year <= QUICK_CONFIG.yearEnd - 2; year += 3) {
  downloadPeriod(year);
  totalExports += QUICK_CONFIG.variables.length * 4; // 4 seasons
}

print('=====================================');
print('✅ Total exports started:', totalExports);
print('📁 Files will appear in Google Drive folder: MACA_QuickStart');
print('⏱️ Estimated time: 5-10 minutes');
print('=====================================');

// Add a preview visualization
var previewYear = QUICK_CONFIG.yearStart;
var previewData = collection
  .filterDate(previewYear + '-06-01', previewYear + '-08-31') // Summer
  .filterBounds(region)
  .filter(ee.Filter.eq('model', QUICK_CONFIG.model))
  .filter(ee.Filter.eq('scenario', QUICK_CONFIG.scenario))
  .select('tasmax')
  .mean();

// Temperature visualization
var tempVis = {
  min: 280,
  max: 310,
  palette: ['blue', 'white', 'red']
};

Map.centerObject(region, 8);
Map.addLayer(previewData, tempVis, 'Summer Tasmax ' + previewYear);
Map.addLayer(region, {color: 'red'}, 'Download Region', false);

print('📍 Preview map added - zoom to see summer temperatures');

// ============================================
// NEXT STEPS
// ============================================

print('\n📚 Next Steps:');
print('1. Check Tasks tab for export progress');
print('2. Files will appear in Google Drive/MACA_QuickStart');
print('3. Modify QUICK_CONFIG to download more data:');
print('   - Change years: yearStart and yearEnd');
print('   - Add variables: ["tasmax", "tasmin", "pr", "rhsmax"]');
print('   - Try different models: "MIROC5", "CCSM4", "CanESM2"');
print('   - Change scenario: "historical", "rcp45", "rcp85"');
print('\n4. For full dataset, use maca_seasonal_download.js');