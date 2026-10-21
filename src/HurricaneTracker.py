# %% [markdown]
# ## Hurricane Tracking Workflow
# This notebook selects trackpoints from a features class of trackpoints for a selected storm (season & name), creates a track line, and extracts US counties that intersect that trackline. 
# 
# Fall 2026  
# jordan.heinlein@duke.edu

# %%
#Import package
import arcpy
from pathlib import Path

#Set paths
raw_folder_path = Path.cwd().parent / 'data' / 'raw'
processed_folder_path = Path.cwd().parent / 'data' / 'processed'

#Arcpy environment settings
arcpy.env.workspace = str(raw_folder_path)
arcpy.env.overwriteOutput = True


#Set model layers
ibtracs_NA_points = str(raw_folder_path /'IBTrACS_NA.shp')
usa_counties = 'https://services.arcgis.com/P3ePLMYs2RVChkJx/arcgis/rest/services/USA_Counties_Generalized_Boundaries/FeatureServer/0'
storm_track_points =  "memory\\track_points"
storm_track_line = "memory\\Tracklines"

#%%
# create dictionary of storm names (value is a list) for each season (key)
storm_dict = {}

# Loop through each season
for storm_season in range(2000,2004):

    # create a list to hold storm names for each season
    storm_names = []

    # Create a list of storm names for a given year using search cursor
    cursor = arcpy.da.SearchCursor(
        in_table= ibtracs_NA_points,
        where_clause= f'SEASON = {storm_season}',
        field_names= ['NAME']
    )

    # iterate through rows in the cursor (ibracs file)
    for row in cursor:
            #get the storm name
            storm_name = row[0]
            #append only unique storm names (no duplicates) and storms not unnamed
            if not storm_name in storm_names and storm_name != 'UNNAMED':
                    storm_names.append(storm_name)

    del(cursor)

    # add key:value pairs to the empty dictionary
    storm_dict[storm_season] = storm_names


# %% [markdown]
# #### Select point features corresponding to a specific storm (season & name)

# %%
#Select points for a given storm
arcpy.analysis.Select(
    in_features=ibtracs_NA_points, 
    out_feature_class=storm_track_points, 
    where_clause=f"SEASON = {storm_season} And NAME = '{storm_name}'"
)

# %% [markdown]
# #### Connect Points to a Track line

# %%
#Connect point to a track line
arcpy.management.PointsToLine(
    Input_Features=storm_track_points,
    Output_Feature_Class=storm_track_line,
    Sort_Field='ISO_TIME'
)

# %% [markdown]
# #### Select Counties Intersecting Point

# %%
#Select intersecting counties
select_output = arcpy.management.SelectLayerByLocation(
    in_layer=usa_counties, 
    overlap_type="INTERSECT", 
    select_features=storm_track_line, 
    )
select_result = select_output.getOutput(0)

#%%

# count the selected counties, save output to variable as integer
county_count = int(arcpy.management.GetCount(select_result).getOutput(0))

