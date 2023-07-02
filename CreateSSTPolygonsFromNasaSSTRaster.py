import arcpy
import os

# Input folder
input_folder = r"C:\Users\gis\Desktop\CVD_Deaths_Project\requested_files"

# Output folder
output_folder = r"C:\Users\gis\Desktop\CVD_Deaths_Project\int_SST"

# Create the output folder if it doesn't exist
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# Walk through the input folder and find all .nc files
nc_files = []
for root, dirs, files in os.walk(input_folder):
    for file in files:
        if file.endswith(".nc"):
            nc_files.append(os.path.join(root, file))

# Loop through each .nc file
for nc_file in nc_files:
    # Extract the file name without the extension
    file_name = os.path.splitext(os.path.basename(nc_file))[0]

    # Create the NetCDF raster layer
    temp_raster_layer = arcpy.MakeNetCDFRasterLayer_md(nc_file, "sst", "lon", "lat", file_name)

    # Define the output raster name with underscores instead of dots
    output_raster = "Int_" + file_name.replace(".", "_") + ".tif"

    # Define the output path
    output_path = os.path.join(output_folder, output_raster)

    # Save the temporary raster layer as an integer TIFF
    arcpy.CopyRaster_management(temp_raster_layer, output_path, pixel_type="32_BIT_SIGNED")

# Input folder containing the int rasters
input_folder = r"C:\Users\gis\Desktop\CVD_Deaths_Project\int_SST"

# Output folder for the reclassified rasters
output_folder = r"C:\Users\gis\Desktop\CVD_Deaths_Project\r_SST"

# Reclassification ranges
reclass_ranges = "-1 7 1; 7 11 2; 11 14 3; 14 17 4; 17 20 5; 20 23 6; 23 25 7; 25 27 8; 27 31 9; 31 9999 10"

# Create the output folder if it doesn't exist
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# Walk through the input folder and find all raster files
raster_files = []
for root, dirs, files in os.walk(input_folder):
    for file in files:
        if file.endswith(".tif"):
            raster_files.append(os.path.join(root, file))

# Loop through each raster file
for raster_file in raster_files:
    # Extract the file name without the extension
    file_name = os.path.splitext(os.path.basename(raster_file))[0]

    # Perform reclassification
    out_raster = arcpy.sa.Reclassify(raster_file, "VALUE", reclass_ranges, "DATA")

    # Define the output raster name
    output_raster = "R_" + file_name + ".tif"

    # Define the output path
    output_path = os.path.join(output_folder, output_raster)

    # Save the reclassified raster
    out_raster.save(output_path)

# Input folder containing the reclassified rasters
input_folder = r"C:\Users\gis\Desktop\CVD_Deaths_Project\r_SST"

# Output geodatabase for the polygons
output_gdb = r"C:\Users\gis\Desktop\CVD_Deaths_Project\sst_polygons.gdb"

# Create the output geodatabase if it doesn't exist
if not arcpy.Exists(output_gdb):
    arcpy.CreateFileGDB_management(os.path.dirname(output_gdb), os.path.basename(output_gdb))

# Walk through the input folder and find all raster files
raster_files = []
for root, dirs, files in os.walk(input_folder):
    for file in files:
        if file.endswith(".tif"):
            raster_files.append(os.path.join(root, file))

# Loop through each raster file
for raster_file in raster_files:
    # Extract the file name without the extension
    file_name = os.path.splitext(os.path.basename(raster_file))[0]

    # Remove invalid characters from the file name
    output_fc_name = "Poly_" + arcpy.ValidateTableName(file_name, output_gdb)

    # Define the output feature class path
    output_fc_path = os.path.join(output_gdb, output_fc_name)

    # Convert the raster to polygons
    arcpy.RasterToPolygon_conversion(raster_file, output_fc_path, "SIMPLIFY", "Value", "MULTIPLE_OUTER_PART", None)

gdb_path = r"C:\Users\gis\Desktop\CVD_Deaths_Project\sst_polygons.gdb"
raster_folder = r"C:\Users\gis\Desktop\CVD_Deaths_Project\int_SST"
output_gdb_folder = r"C:\Users\gis\Desktop\CVD_Deaths_Project"
output_gdb_name = "Zonal_Stat.gdb"

# Create the output geodatabase if it doesn't exist
output_gdb = os.path.join(output_gdb_folder, output_gdb_name)
if not arcpy.Exists(output_gdb):
    arcpy.CreateFileGDB_management(output_gdb_folder, output_gdb_name)

# Set the workspace to the geodatabase
arcpy.env.workspace = gdb_path

# Iterate through feature classes in the geodatabase
feature_classes = arcpy.ListFeatureClasses()
for fc in feature_classes:
    # Get the feature class name without the extension
    fc_name = os.path.splitext(fc)[0]

    # Get the matching raster name with 15 characters from the back
    matching_raster_suffix = fc_name[-15:]

    # Find the matching raster in the specified folder
    matching_raster = None
    for root, dirs, files in os.walk(raster_folder):
        for file in files:
            if file.endswith(".tif") and file.endswith(matching_raster_suffix + ".tif"):
                matching_raster = os.path.join(root, file)
                break
        if matching_raster:
            break

    if matching_raster:
        # Define the output table name with the "STAT_" prefix
        output_table_name = "STAT_" + fc_name

        # Perform zonal statistics as a table
        output_table = os.path.join(output_gdb, output_table_name)
        arcpy.sa.ZonalStatisticsAsTable(fc, "gridcode", matching_raster, output_table, "DATA", "MEAN", "CURRENT_SLICE", [90], "AUTO_DETECT", "ARITHMETIC", 360)

        # Print the output table path
        print("Zonal statistics table created:", output_table)
    else:
        print("Matching raster not found for:", fc_name)

gdb_path = r"C:\Users\gis\Desktop\CVD_Deaths_Project\sst_polygons.gdb"
tables_folder = r"C:\Users\gis\Desktop\CVD_Deaths_Project\Zonal_Stat.gdb"

# Set the workspace to the geodatabase
arcpy.env.workspace = gdb_path

# List feature classes in the geodatabase
feature_classes = arcpy.ListFeatureClasses()

# List tables in the tables geodatabase
arcpy.env.workspace = tables_folder
tables = arcpy.ListTables()

# Iterate through feature classes
for fc in feature_classes:
    # Get the feature class name
    fc_name = os.path.basename(fc)
    fc_suffix = fc_name[-25:]  # Get the last 25 characters
    
    # Find the matching table with the same suffix
    matching_table = next((table for table in tables if table.endswith(fc_suffix)), None)

    if matching_table:
        # Create the input and output paths for the join
        input_feature_path = fc
        input_table_path = os.path.join(tables_folder, matching_table)
        
        # Perform the join using JoinField
        arcpy.management.JoinField(input_feature_path, "gridcode", input_table_path, "gridcode", None, "NOT_USE_FM", None)
        print(f"Joined {fc_name} with {matching_table}")
    else:
        print(f"No matching table found for {fc_name}")
