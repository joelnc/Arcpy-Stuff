#### File to take cross sections, make maps

## Import modules
import arcpy
import csv
import os
import shutil

## Set workspace
arcpy.env.workspace = r'C:\Users\95218\Documents\ArcGIS\SCM Crediting'

## Create Total IC Layer
# Set local variables
xy_tol = ""

## IC Layers from X:\
ic_comm = "X:\stormdat\public\impervious_surface\Commercial_Impervious.shp"
ic_sf = "X:\stormdat\public\impervious_surface\Singlefamily_Impervious.shp"
ic_other = "X:\stormdat\public\impervious_surface\Impervious_Surface_Other.shp"
ic_ed = "X:\Stormdat\public\streets_buffer\Street_EdgeOfPavement.shp"

## Merge them to...
out_feat = "Comb_IC3.shp"

## Need to do this field mapping thing to get around a write error, suspected
## related to non matching fields in the IC layers to merged. To-do: learn pyth
fieldMappings = arcpy.FieldMappings()
fieldMappings.addTable(ic_comm)
fieldMappings.addTable(ic_sf)
fieldMappings.addTable(ic_other)
fieldMappings.addTable(ic_ed)

for field in fieldMappings.fields:
    if field.name not in ["impervious", "st_area_sh", "Subtheme", "Shape_STAr"]:
        fieldMappings.removeFieldMap(fieldMappings.findFieldMapIndex(field.name))


arcpy.Merge_management([ic_comm, ic_sf, ic_other, ic_ed], out_feat, fieldMappings)

arcpy.Dissolve_management("Comb_IC3.shp", "Comb_IC3_Diss.shp", "","",
                          "MULTI_PART", "DISSOLVE_LINES")

######################### Geometry ##########################################
arcpy.AddField_management("Comb_IC3_Diss.shp", "areaSF", "FLOAT", 16, 1, "",
                          "temp", "NULLABLE", "REQUIRED")

arcpy.CalculateField_management("Comb_IC3_Diss.shp", "areaSF",
                                "!shape.area@squarefeet!", "PYTHON_9.3", "")

