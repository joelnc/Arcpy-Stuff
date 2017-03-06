#### File to take cross sections, make maps
## Import modules
import arcpy
from  csv import reader, writer
import os
import shutil
from itertools import izip

## Set workspace
arcpy.env.workspace = r'C:\Users\95218\Documents\ArcGIS\SCM Crediting'

######################### Set files ##########################################
cityIC = r'C:\Users\95218\Documents\ArcGIS\sde\DissCityIC.shp'
buildingIC = r'C:\Users\95218\Documents\ArcGIS\SCM Crediting\CityBFPs.shp'
ParcelsShp = r'C:\Users\95218\Documents\ArcGIS\sde\Parcels.shp'
wsheds = r'C:\Users\95218\Documents\ArcGIS\sde\Watershed_Basins.shp'
arcpy.CalculateField_management(ParcelsShp, "areaSF",
                                "!shape.area@squarefeet!", "PYTHON_9.3", "")

outws = r'C:\temp'
count = 1

fid = []
totalIc = []
parArea = []
buildIc = []
pid = []

arcpy.Delete_management(in_memory_feature_0)
del in_memory_feature_0
shutil.rmtree(r'c:\temp')
os.makedirs(r'c:\temp')
tempBuild = os.path.join(outws, "tempBuild") 
tempTotal = os.path.join(outws, "tempTotal") 

#start = time.time()
with arcpy.da.SearchCursor(wsheds, ["SHAPE@", "TILE_NAME"]) as cursor0:
    ## Outer loop over watersheds
    for row0 in cursor0:
        in_memory_feature_0 = "in_memory\\wshed"

        tempWBld = os.path.join(outws, "tempWBld") 
        tempWIC = os.path.join(outws, "tempWIC") 
        tempWParc = os.path.join(outws, "tempWParc")

        geom0 = row0[0]
        name0 = row0[1]
        arcpy.CopyFeatures_management(geom0, in_memory_feature_0)
        arcpy.Clip_analysis(buildingIC, in_memory_feature_0, tempWBld)
        arcpy.Clip_analysis(ParcelsShp, in_memory_feature_0, tempWParc)
        arcpy.Clip_analysis(cityIC, in_memory_feature_0, tempWIC)
        arcpy.CalculateField_management(r'c:\temp\tempWBld.shp', "areaSF",
                                        "!shape.area@squarefeet!", "PYTHON_9.3", "")
        arcpy.CalculateField_management(r'c:\temp\tempWIC.shp', "areaSF",
                                        "!shape.area@squarefeet!", "PYTHON_9.3", "")
        arcpy.CalculateField_management(r'c:\temp\tempWParc.shp', "areaSF",
                                        "!shape.area@squarefeet!", "PYTHON_9.3", "")
        arcpy.Delete_management(in_memory_feature_0)

        fid = []
        totalIc = []
        parArea = []
        buildIc = []
        pid = []







        
        del tempWBld
        del tempWIC
        del tempWParc
        print name0
        shutil.rmtree(r'c:\temp')
        os.makedirs(r'c:\temp')

#############################################################################
#############################################################################
        


        
        

with arcpy.da.SearchCursor(ParcelsShp, ["FID", "SHAPE@", "areaSF", "pid"]) as cursor:
    for row in cursor:
        ## Add to the fid list
        fid.append(row[0])

        name = row[0]
        geom = row[1]
        in_memory_feature = "in_memory\\" + "v" + str(name)

        print "Parcel: " + str(row[3]) # misc print out
        arcpy.CopyFeatures_management(geom, in_memory_feature)
        arcpy.Clip_analysis(buildingIC, in_memory_feature, tempBuild)
        arcpy.Clip_analysis(cityIC, in_memory_feature, tempTotal)
        arcpy.management.Delete(in_memory_feature)
           
        arcpy.CalculateField_management(r'c:\temp\tempBuild.shp', "areaSF",
                                        "!shape.area@squarefeet!", "PYTHON_9.3", "")
        arcpy.CalculateField_management(r'c:\temp\tempTotal.shp', "areaSF",
                                        "!shape.area@squarefeet!", "PYTHON_9.3", "")

        ## Deal with buildings
        geometriesB = arcpy.CopyFeatures_management(r'c:\temp\tempBuild.shp',
                                                   arcpy.Geometry())
      
        if len(geometriesB)==0: # if no buildings...
            print "No Buildings..."
            buildIc.append(0) # no buildings, write 0
        else:
            totBld = 0 # init building sum
            for building in range(0, len(geometriesB)): # for each bld, sum
                totBld = totBld + geometriesB[building].getArea("PLANAR", "SQUAREFEET")
            
            print str(len(geometriesB)) + " Buildings, sqft = " + str(totBld)
            buildIc.append(totBld) # write total building ic

        ## Deal with total ic
        geometriesT = arcpy.CopyFeatures_management(r'c:\temp\tempTotal.shp',
                                                   arcpy.Geometry())
        if len(geometriesT)==0:
            print "No IC?????..."
            totalIc.append(0) # no buildings, write 0
        else:
            totIc = 0
            for icThing in range(0, len(geometriesT)):
                totIc = totIc + geometriesT[icThing].getArea("PLANAR", "SQUAREFEET")
            print "Tot. sqft = " + str(totIc)
            totalIc.append(totIc) # write total building ic

        ## Parcel Area......
        parArea.append(row[2])
        print "Parcel area = " + str(row[2])
        print "/********/********/********/"

        ## Parcel Area......
        pid.append(row[2])
       
        if count==20:
            break
        #del tempBuild
        #del tempTotal
        count = count + 1
        shutil.rmtree(r'c:\temp')
        os.makedirs(r'c:\temp')
end = time.time()
print(end-start)


## Wrap into list of lists to write to csv, to send to R
listOfLists = [fid, parArea, totalIc, buildIc, pid]

## Write the lists out to a csv
with open("parcelICData.csv", "wb") as f:
    writer = csv.writer(f)
    writer.writerows(listOfLists)
        

## Clunky, open file, transpose, write out
a = izip(*csv.reader(open("parcelICData.csv", "rb")))
csv.writer(open("parcelICData_t.csv", "wb")).writerows(a)
    
