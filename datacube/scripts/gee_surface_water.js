/*****************  Annual Surface-Water Extent : Black Hills  *****************/

/* 0.  AOI & year range */
var AOI         = ee.Geometry.Rectangle([-104.705, 43.480, -103.264, 44.652]);
var START_YEAR  = 1984;          // first year in dataset
var END_YEAR    = 2021;          // last year in v1.4

/* 1.  Load the JRC Yearly History collection */
var yearly = ee.ImageCollection('JRC/GSW1_4/YearlyHistory')   // 30 m :contentReference[oaicite:0]{index=0}
               .filterBounds(AOI);

/* 2.  Loop through years and export a binary water mask */
for (var yr = START_YEAR; yr <= END_YEAR; yr++) {

  // grab the single-year image
  var img = yearly
              .filter(ee.Filter.eq('system:index', yr.toString()))
              .first()
              .select('waterClass');        // values: 0,1,2,3

  // mask: 1 = water (classes 2 or 3), 0 = land / nodata
  var waterMask = img
                    .updateMask( img.eq(2).or(img.eq(3)) )
                    .rename('water_extent')
                    .uint8();               // keeps file size small

  Export.image.toDrive({
    image:          waterMask.clip(AOI),
    description:    'SurfWater_' + yr,
    folder:         'EarthEngine_SurfaceWater',
    fileNamePrefix: 'SurfaceWater_BlackHills_' + yr,
    region:         AOI,
    scale:          30,
    maxPixels:      1e13
  });
}

/* Optional quick-look */
Map.centerObject(AOI, 8);
Map.addLayer(yearly
              .filter(ee.Filter.eq('system:index', '2021'))
              .first()
              .select('waterClass')
              .clip(AOI),
            {min:1, max:3, palette:['grey','white','cyan','blue']},
            '2022 waterClass');
