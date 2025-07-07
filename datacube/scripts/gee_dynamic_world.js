/*********************  Dynamic World Composite: Black Hills  *********************/
/* Bounding box (W, S, E, N) */
var BLACK_HILLS_COORDS = [-104.705, 43.480, -103.264, 44.652];
var aoi = ee.Geometry.Rectangle(BLACK_HILLS_COORDS);

/* -----------------------------------------------------------------------
   1.  CONFIGURE TIME RANGE
   -------------------------------------------------------------------- */
var START_DATE = '2024-01-01';
var END_DATE   = '2024-12-31';   // change as needed

/* -----------------------------------------------------------------------
   2.  LOAD & FILTER DYNAMIC WORLD
   -------------------------------------------------------------------- */
var dw = ee.ImageCollection('GOOGLE/DYNAMICWORLD/V1')      // nine-class land-cover dataset
            .filterBounds(aoi)
            .filterDate(START_DATE, END_DATE);

/* -----------------------------------------------------------------------
   3.  CREATE TWO POSSIBLE COMPOSITES
   -------------------------------------------------------------------- */
// (A) “Most-common class” composite (mode of the ‘label’ band)
var labelMode = dw.select('label')
                  .reduce(ee.Reducer.mode())
                  .rename('dw_mode');

// (B) “Median probability” composite (per-class probability median)
var probMedian = dw.select(['water','trees','grass','flooded_vegetation',
                            'crops','shrub_and_scrub','built_area',
                            'bare_ground','snow_and_ice'])
                   .median()
                   .rename(['water','trees','grass','flood','crops',
                            'shrub','built','bare','snow']);

/* -----------------------------------------------------------------------
   4.  VISUALIZE  (palette follows the Dynamic World legend)
   -------------------------------------------------------------------- */
var palette = ['#419BDF','#397D49','#88B053','#7A87C6',
               '#E49635','#DFC35A','#C4281B','#A59B8F','#B39FE1'];

Map.centerObject(aoi, 8);
Map.addLayer(labelMode.clip(aoi),
             {min: 0, max: 8, palette: palette},
             'DW Mode Composite (' + START_DATE + ' → ' + END_DATE + ')', true);
             
//  Uncomment to view median-probability of the “trees” class
//  Map.addLayer(probMedian.select('trees').clip(aoi),
//               {min: 0, max: 1, palette: ['white','green']},
//               'Median Tree Probability');

/* -----------------------------------------------------------------------
   5.  EXPORT  (edit description / scale / destination as desired)
   -------------------------------------------------------------------- */
Export.image.toDrive({
  image: labelMode.clip(aoi),      // swap for probMedian if preferred
  description: 'DW_BlackHills_' + START_DATE + '_' + END_DATE + '_mode',
  folder: 'EarthEngineExports',
  fileNamePrefix: 'DW_BlackHills_mode',
  region: aoi,
  scale: 10,                       // Sentinel-2 native resolution
  maxPixels: 1e13
});
/* --------------------------------------------------------------------- */
