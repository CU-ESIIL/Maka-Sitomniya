/********************  Annual Burned-Area TIFFs : Black Hills  ********************/

/* ---------------------------  0.  CONFIG  ------------------------------------ */
var AOI         = ee.Geometry.Rectangle([-104.705, 43.480, -103.264, 44.652]);
var START_YEAR  = 2001;                 // first full year of both products
var END_YEAR    = 2024;                 // FireCCI ends 2024; MCD64A1 continues

/***** pick ONE burned-area product *****/
var DATASET = 'MODIS/061/MCD64A1';   // or  'ESA/CCI/FireCCI/5_1'
var SCALE   = (DATASET.indexOf('FireCCI') > -1) ? 250 : 500;

/*  rest of the script unchanged … */
var burns = ee.ImageCollection(DATASET)
               .select('BurnDate')        // both products use this band
               .filterBounds(AOI);


/* --------------------------- 2. EXPORT LOOP ------------------------------ */
for (var yr = START_YEAR; yr <= END_YEAR; yr++) {

  var yrStart  = ee.Date.fromYMD(yr, 1, 1);
  var yrEnd    = yrStart.advance(1, 'year');

  // raw annual mosaic
  var annualRaw = burns
                    .filterDate(yrStart, yrEnd)
                    .mosaic();

  // mask out unburned pixels (BurnDate == 0)
  var annual = annualRaw
                 .updateMask(annualRaw.gt(0))   // keep only pixels with a burn date
                 .uint16();                     // 0–366 range fits in 16-bit

  Export.image.toDrive({
    image:            annual.clip(AOI),
    description:      'BurnedArea_' + yr,
    folder:           'EarthEngine_BurnedArea',
    fileNamePrefix:   'BurnedArea_BlackHills_' + yr,
    region:           AOI,
    scale:            SCALE,
    maxPixels:        1e13
  });
}
