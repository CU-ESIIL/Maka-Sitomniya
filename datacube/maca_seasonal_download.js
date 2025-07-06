/**
 * MACA v2 Seasonal Download Script for Google Earth Engine
 * 
 * This script downloads MACA v2 climate data with seasonal preservation,
 * creating 3-year seasonal means for comprehensive climate analysis.
 * 
 * Usage:
 * 1. Copy this script to Google Earth Engine Code Editor
 * 2. Modify parameters as needed
 * 3. Run the script
 * 4. Check Tasks tab for export progress
 * 5. Files will appear in your Google Drive
 */

// ============================================================================
// CONFIGURATION
// ============================================================================

// Define your region of interest (Black Hills example)
var blackHills = ee.Geometry.Rectangle([-104.705, 43.480, -103.264, 44.652]);

// You can also draw your own region using the geometry tools
// var region = geometry; // Use drawn geometry

// Core parameters
var EXPORT_FOLDER = 'MACA_Seasonal_3Year'; // Google Drive folder
var SCALE = 4000; // 4km resolution
var MAX_PIXELS = 1e9; // Maximum pixels per export

// Variables to download
var VARIABLES = [
  'tasmax',  // Maximum temperature
  'tasmin',  // Minimum temperature
  'pr',      // Precipitation
  // Extended variables (uncomment to include):
  // 'rhsmax',  // Maximum relative humidity
  // 'rhsmin',  // Minimum relative humidity
  // 'huss',    // Specific humidity
  // 'was',     // Wind speed
  // 'rsds'     // Downward shortwave radiation
];

// Climate models
var MODELS = [
  'GFDL-ESM2M',
  // Add more models as needed:
  // 'MIROC5',
  // 'CCSM4',
  // 'CanESM2',
  // 'CNRM-CM5'
];

// Scenarios
var SCENARIOS = {
  'historical': {start: 1950, end: 2005},
  'rcp45': {start: 2006, end: 2099},
  'rcp85': {start: 2006, end: 2099}
};

// ============================================================================
// SEASONAL DEFINITIONS
// ============================================================================

var SEASONS = {
  'DJF': {
    months: [12, 1, 2],
    name: 'Winter',
    monthFilter: function(img) {
      var month = ee.Date(img.get('system:time_start')).get('month');
      return ee.List([12, 1, 2]).contains(month);
    }
  },
  'MAM': {
    months: [3, 4, 5],
    name: 'Spring',
    monthFilter: function(img) {
      var month = ee.Date(img.get('system:time_start')).get('month');
      return ee.List([3, 4, 5]).contains(month);
    }
  },
  'JJA': {
    months: [6, 7, 8],
    name: 'Summer',
    monthFilter: function(img) {
      var month = ee.Date(img.get('system:time_start')).get('month');
      return ee.List([6, 7, 8]).contains(month);
    }
  },
  'SON': {
    months: [9, 10, 11],
    name: 'Fall',
    monthFilter: function(img) {
      var month = ee.Date(img.get('system:time_start')).get('month');
      return ee.List([9, 10, 11]).contains(month);
    }
  }
};

// ============================================================================
// MAIN FUNCTIONS
// ============================================================================

// Load MACA collection
var collection = ee.ImageCollection('IDAHO_EPSCOR/MACAv2_METDATA');

/**
 * Download seasonal means for a 3-year period
 */
function downloadSeasonalPeriod(startYear, endYear, variable, model, scenario, season, seasonDef) {
  // Create date range
  var startDate = startYear + '-01-01';
  var endDate = endYear + '-12-31';
  
  // Filter collection
  var filtered = collection
    .filterDate(startDate, endDate)
    .filterBounds(region || blackHills)
    .filter(ee.Filter.eq('model', model))
    .filter(ee.Filter.eq('scenario', scenario))
    .select(variable)
    .filter(seasonDef.monthFilter);
  
  // Check if data exists
  var count = filtered.size();
  
  // Calculate seasonal mean
  var seasonalMean = filtered.mean();
  
  // Add metadata
  seasonalMean = seasonalMean.set({
    'variable': variable,
    'model': model,
    'scenario': scenario,
    'season': season,
    'start_year': startYear,
    'end_year': endYear,
    'description': variable + ' ' + seasonDef.name + ' mean for ' + startYear + '-' + endYear
  });
  
  // Create filename
  var filename = variable + '_' + model + '_' + scenario + '_' + 
                 startYear + '_' + endYear + '_' + season;
  
  // Export to Drive
  Export.image.toDrive({
    image: seasonalMean,
    description: filename,
    folder: EXPORT_FOLDER,
    fileNamePrefix: filename,
    scale: SCALE,
    region: region || blackHills,
    maxPixels: MAX_PIXELS,
    fileFormat: 'GeoTIFF',
    formatOptions: {
      cloudOptimized: true
    }
  });
  
  return filename;
}

/**
 * Process all time periods for a given configuration
 */
function processAllPeriods(variable, model, scenario) {
  var scenarioInfo = SCENARIOS[scenario];
  var startYear = scenarioInfo.start;
  var endYear = scenarioInfo.end;
  
  var taskCount = 0;
  var tasks = [];
  
  // Process each 3-year period
  for (var year = startYear; year <= endYear - 2; year += 3) {
    var periodEnd = Math.min(year + 2, endYear);
    
    // Process each season
    Object.keys(SEASONS).forEach(function(season) {
      var filename = downloadSeasonalPeriod(
        year, 
        periodEnd, 
        variable, 
        model, 
        scenario, 
        season,
        SEASONS[season]
      );
      
      tasks.push(filename);
      taskCount++;
    });
  }
  
  print('Started ' + taskCount + ' tasks for ' + variable + ' ' + model + ' ' + scenario);
  return tasks;
}

// ============================================================================
// EXECUTION
// ============================================================================

print('Starting MACA v2 Seasonal Downloads');
print('Region:', region || blackHills);
print('Variables:', VARIABLES);
print('Models:', MODELS);
print('Scenarios:', Object.keys(SCENARIOS));

var totalTasks = 0;
var allTasks = [];

// Process each combination
VARIABLES.forEach(function(variable) {
  MODELS.forEach(function(model) {
    Object.keys(SCENARIOS).forEach(function(scenario) {
      var tasks = processAllPeriods(variable, model, scenario);
      allTasks = allTasks.concat(tasks);
      totalTasks += tasks.length;
    });
  });
});

print('=====================================');
print('TOTAL EXPORT TASKS STARTED:', totalTasks);
print('=====================================');
print('Check the Tasks tab to monitor progress');
print('Files will appear in Google Drive folder:', EXPORT_FOLDER);

// ============================================================================
// HELPER FUNCTIONS
// ============================================================================

/**
 * List available data for verification
 */
function checkDataAvailability() {
  var sample = collection
    .filterBounds(region || blackHills)
    .first();
  
  if (sample) {
    print('Available bands:', sample.bandNames());
    print('Sample image info:', sample);
  } else {
    print('No data found for the specified region');
  }
}

// Uncomment to check data availability
// checkDataAvailability();

/**
 * Create a preview visualization
 */
function previewData(variable, model, scenario, year) {
  var preview = collection
    .filterDate(year + '-01-01', year + '-12-31')
    .filterBounds(region || blackHills)
    .filter(ee.Filter.eq('model', model))
    .filter(ee.Filter.eq('scenario', scenario))
    .select(variable)
    .mean();
  
  var visParams = {
    min: variable === 'pr' ? 0 : 250,
    max: variable === 'pr' ? 10 : 310,
    palette: variable === 'pr' ? 
      ['white', 'blue', 'darkblue'] : 
      ['blue', 'white', 'red']
  };
  
  Map.centerObject(region || blackHills, 8);
  Map.addLayer(preview, visParams, variable + ' ' + year);
}

// Uncomment to preview data
// previewData('tasmax', 'GFDL-ESM2M', 'rcp45', 2020);

print('Script completed. Exports are running in the background.');