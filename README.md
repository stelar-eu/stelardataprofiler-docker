# Welcome to the KLMS Tool version of stelardataprofiler

[stelardataprofiler](https://github.com/stelar-eu/data-profiler) is a Python library providing various functions for profiling different types of data and files.
# Quick start

Please see the provided [notebooks](https://github.com/stelar-eu/stelardataprofiler-docker/tree/main/notebooks).

# Instructions

## Profiler Types and Their Supported File Extensions

| Profiler Type | Supported File Extensions               |
|---------------|---------------------------------------|
| timeseries    | `.csv`, `.xlsx`, `.xls`  (used if [`ts_mode`](#ts_mode) parameter is `False`)              |
| tabular       | `.csv`, `.xlsx`, `.xls`, `.shp` (used if [`ts_mode`](#ts_mode) parameter is `True`)      |
| raster        | `.tif`, `.tiff`, `.img`, `.vrt`, `.nc`, `.grd`, `.asc`, `.jp2`, `.hdf`, `.hdr`, `.bil`, `.png` |
| textual       | `.txt`                                |
| hierarchical  | `.json`                               |
| rdfGraph      | `.ttl`, `.turtle`, `.rdf`, `.owl`, `.xml`, `.nt`, `.nq`, `.trig`, `.jsonld`, `.n3`             |

## Profile
### Input
To run stelardataprofiler, via STELAR KLMS API, the following input JSON structure is expected:

```json
{
  "process_id": "<PROCESS_ID>",
  "inputs": {
    "data": [
        "<RESOURCE_UUID>"
    ],
    "type_detection_file": [
        "<RESOURCE_UUID_2>"
    ]
  },
  "outputs": {
    "profile": {
        "url":"s3://<BUCKET_NAME>/temp/profile.json",
        "resource": {
            "name": "stelardataprofiler Profile of <RESOURCE_UUID>",
            "relation": "profile",
            "format": "json"
        }
    }
  },
  "datasets":{
    "d0": "<DATASET_UUID>" 
  },
  "parameters": {
        "header": 0,
        "...": "additional parameters can be defined here"
  }
}
```

#### Input
- **`data`** *(str or list[str], required)*  
  Path to the file. Each profiler type handles different file extensions.
  
  **_NOTE:_**  Multiple files are allowed only for the textual and raster profile types.  
  Also, in the case of tabular profiler type where we have shp file the user needs to provide a list of resource uuids that contain **shp**, **shx**, **dbf**, **cpg** and **prj** files with the same name. The first resource in the list must be have **shp** file extension.

- **`type_detection_file`** *(str, optional, default=None)*  
Path to the **types JSON file**. If this file is **not provided**, the types will be **automatically detected**.  
For more information on how to generate this file, click [here](https://github.com/stelar-eu/stelardataprofiler-docker/blob/main/README.md#Type-Detection).

   **_WARNING:_** Only in the cases of **tabular** and **timeseries** profiler types.

#### Parameters  
- **`profile_type`** *(str, optional, default=None)*  
  Specifies the profile type that will be used.     
  If not provided, the profile type is automatically detected based on the file extension of the first provided input file.

- **`sep`** *(str, optional, default=",")* **(tabular, timeseries)**    
  The delimiter used to separate values in the tabular and timeseries data.    
  If not specified, the default is comma(,).

- **`header`** *(int or bool, optional, default=0)* **(tabular, timeseries)**  
  The row number that contains the header of the tabular and timeseries  data.   
  If header is true then header=0 and if header is false then header=None.   
  If not provided, the default is 0.  

- **`light_mode`** *(bool, optional, default=false)*  **(tabular, timeseries)**   
  If enabled, the profiling will be done in a light mode, which is faster but less detailed.

- **`num_cat_perc_threshold`** *(float, optional, default=0.5)*  **(tabular, timeseries)**   
  The threshold for a column to be considered categorical.    
  If the percentage of unique values in a column is less than this value, the column will be considered categorical.    
  If not specified, the default is 0.5 (50%). 

  **_NOTE:_** Must be between 0 and 1.

- **`max_freq_distr`** *(int, optional, default=10)*  **(tabular, timeseries)**   
  Top-K most frequent values to be displayed in the frequency distribution.   
  If not specified, the default is 10. 

- **`ts_mode`** *(bool, optional, default=false)*  **(timeseries)**   
  Whether to treat data as timeseries 
  If not specified, the default is false and the data are treated as tabular.

- **`time_column`** *(str, optional, default="date")*  **(timeseries)**   
  Datetime column for timeseries. If not specified, the default is "date".

- **`crs`** *(str, optional, default="EPSG:4326")*  **(tabular)**   
  Coordinate Reference System used for interpreting geospatial data.
  If not specified, the default is "EPSG:4326".

- **`eps_distance`** *(int, optional, default=1000)*  **(tabular)**   
  Distance tolerance (in meters) for spatial clustering in geometry heatmaps  
  If not specified, the default is 1000.

- **`extra_geometry_columns`** *(list[dict], optional, default=[])*  **(tabular)**   
  Additional geometry columns to consider.
  If not specified, the default is [].

  **_EXAMPLE:_** 
  ```json
  "extra_geometry_columns" : [
        {
            "longitude": "lon_column_name_1",
            "latitude": "lon_column_name_1"
        },
        {
            "longitude": "lon_column_name_2",
            "latitude": "lon_column_name_2"
        }
    ]
  ```

- **`serialization`** *(str, optional, default="turtle")*  **(rdfGraph)**   
  The format of the rdf file. If not specified, the default is "turtle". 

  **_NOTE:_** If profile_type is None then serialization is identified based on the file extension. Extensions like **.ttl** and **.turtle** use the **turtle** serialization format, while **.rdf**, **.owl**, and **.xml** use **xml**. The **.nt** extension corresponds to **nt**, and **.nq** corresponds to **nquads**. Files with **.trig** use the **trig** format, **.jsonld** uses **json-ld**, and **.n3** uses the **n3** format.

### Output

The output of stelardataprofiler has the following format:

```json
{
    "message": "stelardataprofiler Tool Executed Successfully",
	"output": {
		"profile": "path_of_profile_file"
    },
	"metrics": {	
        "time": 5.8976,
    },
	"status": "success"
}
```

## Type Detection 
In tabular and timeseries, the profiler provides the [type detection mode](https://github.com/stelar-eu/data-profiler/tree/main?tab=readme-ov-file#type-detection---customize-the-profiler).    
This particular mode produces a json file that the user can modify.      
The user then may provide this modified json file as **type_detection_file** to the input JSON structure of the standard stelardataprofiler.
### Input
To run stelardataprofiler type detection mode, via STELAR KLMS API, the following input JSON structure is expected:

```json
{
  "process_id": "<PROCESS_ID>",
  "inputs": {
    "data": [
        "<RESOURCE_UUID>"
    ]
  },
  "outputs": {
    "types": {
        "url":"s3://<BUCKET_NAME>/temp/types_dict.json",
        "resource": {
            "name": "stelardataprofiler extracted types of <RESOURCE_UUID>",
            "relation": "profile_type_detection",
            "format": "json"
        }
    }
  },
  "datasets":{
    "d0": "<DATASET_UUID>" 
  },
  "parameters": {
        "type_detection_mode": true,
        "ts_mode": false,
        "...": "additional parameters can be defined here"
  }
}
```

#### Input
- **`data`** *(str or list[str], required)*  
  Path to the file. Each profiler type handles different file extensions.
  
  **_NOTE:_**  Multiple files are allowed only for the textual and raster profile types.  
  Also, in the case of tabular profiler type where we have shp file the user needs to provide a list of resource uuids that contain **shp**, **shx**, **dbf**, **cpg** and **prj** files with the same name. The first resource in the list must be have **shp** file extension.

#### Parameters  
- **`type_detection_mode`** *(str, required, must be true)*  
  This parameter specifies that the tool executes type detection mode and produces a json file with the automatically detected types of each column. The user may change the detected types. If not specified, the default is false and profiling is executed.

- **`profile_type`** *(str, optional, default=None)*  
  Specifies the profile type that will be used.     
  If not provided, the profile type is automatically detected based on the file extension of the first provided input file.

- **`sep`** *(str, optional, default=",")* **(tabular, timeseries)**    
  The delimiter used to separate values in the tabular and timeseries data.    
  If not specified, the default is comma(,).

- **`header`** *(int or bool, optional, default=0)* **(tabular, timeseries)**  
  The row number that contains the header of the tabular and timeseries  data.   
  If header is true then header=0 and if header is false then header=None.   
  If not provided, the default is 0.  

- **`light_mode`** *(bool, optional, default=false)*  **(tabular, timeseries)**   
  If enabled, the profiling will be done in a light mode, which is faster but less detailed.

- **`num_cat_perc_threshold`** *(float, optional, default=0.5)*  **(tabular, timeseries)**   
  The threshold for a column to be considered categorical.    
  If the percentage of unique values in a column is less than this value, the column will be considered categorical.    
  If not specified, the default is 0.5 (50%). 

  **_NOTE:_** Must be between 0 and 1.

- **`max_freq_distr`** *(int, optional, default=10)*  **(tabular, timeseries)**   
  Top-K most frequent values to be displayed in the frequency distribution.   
  If not specified, the default is 10. 

- **`ts_mode`** *(bool, optional, default=false)*  **(timeseries)**   
  Whether to treat data as timeseries 
  If not specified, the default is false and the data are treated as tabular.

- **`time_column`** *(str, optional, default="date")*  **(timeseries)**   
  Datetime column for timeseries. If not specified, the default is "date".

- **`crs`** *(str, optional, default="EPSG:4326")*  **(tabular)**   
  Coordinate Reference System used for interpreting geospatial data.
  If not specified, the default is "EPSG:4326".

- **`eps_distance`** *(int, optional, default=1000)*  **(tabular)**   
  Distance tolerance (in meters) for spatial clustering in geometry heatmaps  
  If not specified, the default is 1000.

- **`extra_geometry_columns`** *(list[dict], optional, default=[])*  **(tabular)**   
  Additional geometry columns to consider.
  If not specified, the default is [].

  **_EXAMPLE:_** 
  ```json
  "extra_geometry_columns" : [
        {
            "longitude": "lon_column_name_1",
            "latitude": "lon_column_name_1"
        },
        {
            "longitude": "lon_column_name_2",
            "latitude": "lon_column_name_2"
        }
    ]
  ```

### Output

The output of stelardataprofiler **type detection mode** has the following format:

```json
{
    "message": "stelardataprofiler Tool Executed Successfully",
	"output": {
        "types": "path_of_types_file",
    },
	"metrics": {	
        "time": 0.004813976,
    },
	"status": "success"
}
```

