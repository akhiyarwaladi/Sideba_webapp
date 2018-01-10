import arcpy
import pandas as pd
import numpy as np
from tqdm import *

def predictClass(dataPath, modelPath, outputPath):
	#pth = "C:/DATA_LAPAN/LC81190652016273LGN00"
	rasterarray = arcpy.RasterToNumPyArray(dataPath+"/LC81190652017067RPI00_B6.TIF")
	rasterarray2 = arcpy.RasterToNumPyArray(dataPath+"/LC81190652017067RPI00_B5.TIF")
	rasterarray3 = arcpy.RasterToNumPyArray(dataPath+"/LC81190652017067RPI00_B4.TIF")
	print rasterarray.shape
	print rasterarray2.shape
	print rasterarray3.shape
	print("Change raster format to numpy array")
	data = np.array([rasterarray.ravel(), rasterarray2.ravel(), rasterarray3.ravel()])
	data = data.transpose()
	print data.shape
	import pandas as pd
	print("Change to dataframe format")
	columns = ['band1','band2', 'band3']
	df = pd.DataFrame(data, columns=columns)

	print("Split data to 20 chunks")
	df_arr = np.array_split(df, 20)

	kelasAll = []
	for i in range(len(df_arr)):
	    from sklearn.externals import joblib
	    clf = joblib.load(modelPath) 
	    print ("predicting data chunk-"+str(i))
	    kelas = clf.predict(df_arr[i])
	    dat = pd.DataFrame()
	    dat['kel'] = kelas
	    print ("mapping to integer class")
	    mymap = {'awan':2, 'air':1, 'tanah':2, 'vegetasi':2}
	    dat['kel'] = dat['kel'].map(mymap)

	    band1Array = dat['kel'].values
	    print band1Array.shape
	    band1Array = np.array(band1Array, dtype=np.uint8)
	    print band1Array.shape
	    print ("extend to list")
	    kelasAll.extend(band1Array.tolist())

	del df_arr
	del clf
	del kelas
	del dat
	del band1Array
	del data

	print ("change list to np array")
	kelasAllArray = np.array(kelasAll, dtype=np.uint8)
	print kelasAllArray.shape
	print ("reshaping np array")
	band1 = np.reshape(kelasAllArray, (-1, rasterarray[0].size))
	band1 = band1.astype(np.uint8)

	raster = arcpy.Raster(dataPath+"/LC81190652017067RPI00_B4.TIF")
	inputRaster = dataPath+"/LC81190652017067RPI00_B4.TIF"

	spatialref = arcpy.Describe(inputRaster).spatialReference
	cellsize1  = raster.meanCellHeight
	cellsize2  = raster.meanCellWidth
	extent     = arcpy.Describe(inputRaster).Extent
	pnt        = arcpy.Point(extent.XMin,extent.YMin)

	

	# save the raster
	print ("numpy array to raster ..")
	#out_ras = arcpy.NumPyArrayToRaster(band1, pnt, raster, raster, raster.noDataValue)
	out_ras = arcpy.NumPyArrayToRaster(band1, pnt, cellsize1, cellsize2)
	#out_ras.save(outputPath+"/permWater.tif")
	#arcpy.CheckOutExtension("Spatial")
	print ("define projection ..")
	del raster
	arcpy.CopyRaster_management(out_ras, outputPath+"/permWaterCrr.tif")
	arcpy.DefineProjection_management(outputPath+"/permWaterCrr.tif", spatialref)
