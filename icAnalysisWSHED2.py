#### File to take cross sections, make maps
## Import modules
import arcpy
import csv
import os
import shutil
from itertools import izip

## Set workspace
arcpy.env.workspace = r'C:\Users\95218\Documents\ArcGIS\SCM Crediting'

######################### Set files ##########################################
cityIC = r'C:\Users\95218\Documents\ArcGIS\sde\DissCityIC.shp'
buildingIC = r'C:\Users\95218\Documents\ArcGIS\SCM Crediting\CityBFPs.shp'
ParcelsShp = r'C:\Users\95218\Documents\ArcGIS\sde\ParcelsUnique.shp'
wsheds = r'C:\Users\95218\Documents\ArcGIS\sde\Watershed_Basins6.shp'

outws = r'C:\temp'
outws2 = r'C:\temp2'

count = 1
wCount = 1
fid = []
totalIc = []
parArea = []
buildIc = []
pid = []

#start = time.time()
with arcpy.da.SearchCursor(wsheds, ["SHAPE@", "TILE_NAME"]) as cursor0:
    ## Outer loop over watersheds
    for row0 in cursor0:
        in_memory_feature_0 = "in_memory\\wshed" ## watershed

        geom0 = row0[0] # Shape
        name0 = row0[1] # Name
        arcpy.CopyFeatures_management(geom0, in_memory_feature_0)

        ## Clip to watershed, calc areas (necessary?)
        tempWBld = "in_memory//tempWBld" 
        tempWIC = "in_memory//tempWIC" 
        tempWParc = "in_memory//tempWParc"

        arcpy.Clip_analysis(buildingIC, in_memory_feature_0, tempWBld)
        arcpy.Clip_analysis(ParcelsShp, in_memory_feature_0, tempWParc)
        arcpy.Clip_analysis(cityIC, in_memory_feature_0, tempWIC)

         ## Initialize watershed data lists
        fid = []
        totalIc = []
        parArea = []
        buildIc = []
        pid = []
        del row0
        count = 1
        ## Inner loop (over parcels, within watershed)
        with arcpy.da.SearchCursor(tempWParc,
                                   ["FID", "SHAPE@", "SHAPE_STAr", "taxpid"]) as cursor:
            for row in cursor:
                ## Add to the fid list
                fid.append(row[0])

                name = row[0]
                geom = row[1]
                in_memory_feature = "in_memory\\" + "v" + str(name)

                print "Parcel: " + str(row[3]) + ", " + name0 # misc print out
                arcpy.CopyFeatures_management(geom, in_memory_feature)
                
                tempBuild = "in_memory//tempBuild"
                tempTotal = "in_memory//tempTotal"
                arcpy.Clip_analysis(tempWBld, in_memory_feature, tempBuild)
                arcpy.Clip_analysis(tempWIC, in_memory_feature, tempTotal)

                arcpy.Delete_management(in_memory_feature)
                del in_memory_feature
                                                
                ## Deal with buildings
                geometriesB = arcpy.CopyFeatures_management(tempBuild,
                                                   arcpy.Geometry())
      
                if len(geometriesB)==0: # if no buildings...
                    buildIc.append(0) # no buildings, write 0
                else:
                    totBld = 0 # init building sum
                    for building in range(0, len(geometriesB)): # for each bld, sum
                        totBld = totBld + geometriesB[building].getArea("PLANAR", "SQUAREFEET")
                    buildIc.append(totBld) # write total building ic

                ## Deal with total ic
                geometriesT = arcpy.CopyFeatures_management(tempTotal,
                                                            arcpy.Geometry())
                if len(geometriesT)==0:
                    totalIc.append(0) # no buildings, write 0
                else:
                    totIc = 0
                    for icThing in range(0, len(geometriesT)):
                        totIc = totIc + geometriesT[icThing].getArea("PLANAR", "SQUAREFEET")
                    totalIc.append(totIc) # write total building ic

                ## Parcel Area......
                parArea.append(row[2])

                ## Parcel Area......
                pid.append(row[3])

                #shutil.rmtree(r'c:\temp') ## delete files, not dirs
                arcpy.Delete_management(tempTotal)
                arcpy.Delete_management(tempBuild)

                # if count==20:
                #     arcpy.Delete_management(in_memory_feature_0)
                #     arcpy.Delete_management(tempWBld)
                #     arcpy.Delete_management(tempWIC)
                #     arcpy.Delete_management(tempWParc)
                #     break

                count = count + 1
        ## Wrap into list of lists to write to csv, to send to R
        listOfLists = [fid, parArea, totalIc, buildIc, pid]

        ## Write the lists out to a csv
        with open("parcelICData" + name0 + ".csv", "wb") as f:
            writer = csv.writer(f)
            writer.writerows(listOfLists)

        arcpy.Delete_management(in_memory_feature_0)
        arcpy.Delete_management(tempWBld)
        arcpy.Delete_management(tempWIC)
        arcpy.Delete_management(tempWParc)

        del listOfLists
        del row, cursor

        # if wCount==10:
        #     break
        wCount = wCount + 1


#############################################################################     
#############################################################################     

## Clunky, open file, transpose, write out
#a = izip(*csv.reader(open("parcelICData.csv", "rb")))
#csv.writer(open("parcelICData_t.csv", "wb")).writerows(a)
    
