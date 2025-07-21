import json
import sys
import os
import traceback
from utils.mclient import MinioClient
from time import time
from stelardataprofiler import (
    profile_timeseries,
    profile_tabular,
    profile_raster,
    profile_text,
    profile_hierarchical,
    profile_rdfGraph,
    type_detection,
    read_config,
    write_to_json
)
import pandas as pd


def run(json_blob):
    try:

        minio = json_blob["minio"]

        mc = MinioClient(
            minio["endpoint_url"],
            minio["id"],
            minio["key"],
            secure=True,
            session_token=minio["skey"],
        )
        
        inputs = json_blob["input"]
        parameters = json_blob["parameters"]
        
        # we may have multiple files
        # only the first one is the main file in cases where the profiler runs with one input
        files = inputs["data"]
        
        # take the type_detection json file if given
        td_file = inputs.get("type_detection_file", [None])[0]
        types_dict = None
        if td_file is not None:
            mc.get_object(s3_path=td_file, local_path="types_dict.json")
            types_dict  = read_config("types_dict.json")
        
        # run type_detection mode
        # if true it produces types_dict JSON file instead of profile JSON file
        type_detection_mode = parameters.get("type_detection_mode", False)
        
        # get the parameters for all profiler types
        sep = parameters.get("sep", ",")
        header = parameters.get("header", 0)
        serialization = parameters.get("serialization", "turtle")
        light_mode = parameters.get("light_mode", False)
        num_cat_perc_threshold = parameters.get("num_cat_perc_threshold", 0.5)
        max_freq_distr = parameters.get("max_freq_distr", 10)
        ts_mode = parameters.get("ts_mode", False)
        time_column = parameters.get("time_column", None)
        crs = parameters.get("crs", "EPSG:4326")
        eps_distance = parameters.get("eps_distance", 1000)
        extra_geometry_columns = parameters.get("extra_geometry_columns", None)
        
        # if None then find profile type based on the first file in data
        profile_type = parameters.get("profile_type", None)
        
        local_files = []
        
        for i in range(len(files)):
            ext = os.path.splitext(files[i])[1].lower()
            log = mc.get_object(s3_path=files[i], local_path=f'file_{i}{ext}')
            if 'error' in log:
                raise ValueError(log['error'])
                
            if i == 0:
                if ext in [".xlsx", ".xls"]:
                    file = pd.read_excel(f'file_0{ext}', header=header)
                    file.to_csv('file_0.csv', index=False, header=header, sep=sep)
                    
                    local_files.append(f'file_0.csv') 
                else:
                    local_files.append(f'file_{i}{ext}')
                
                
                if not profile_type:
                    if ext in [".csv", ".xlsx", ".xls", ".shp"]:
                        if ts_mode:
                            profile_type = "timeseries"
                        else:
                            profile_type = "tabular"
                    elif ext in [".txt"]:
                        profile_type = "textual"
                    elif ext in [".json"]:
                        profile_type = "hierarchical"
                    elif ext in [".tif", ".tiff", ".img", ".vrt", ".nc", ".grd", ".asc", ".jp2", ".hdf", ".hdr", ".bil", ".png"]:
                        profile_type = "raster"
                    elif ext in [".ttl", ".turtle", ".rdf", ".owl", ".xml", ".nt", ".nq", ".trig", ".jsonld", ".n3"]:
                        profile_type = "rdfgraph"
                        # Map extensions to serialization formats
                        if ext in [".ttl", ".turtle"]:
                            serialization = "turtle"
                        elif ext in [".rdf", ".owl", ".xml"]:
                            serialization = "xml"
                        elif ext == ".nt":
                            serialization = "nt"
                        elif ext == ".nq":
                            serialization = "nquads"
                        elif ext == ".trig":
                            serialization = "trig"
                        elif ext == ".jsonld":
                            serialization = "json-ld"
                        elif ext == ".n3":
                            serialization = "n3"
                        else:
                            serialization = serialization  # Default to user-given serialization if unknown RDF type
                    else:
                        profile_type = None
                else:
                    profile_type = profile_type.lower()
                    
        t = time()
        if type_detection_mode:
            if profile_type == "timeseries":
                types_dict = type_detection(input_path=local_files[0], header=header, sep=sep, ts_mode=True, ts_mode_datetime_col=time_column)
            elif profile_type == "tabular":
                types_dict = type_detection(input_path=local_files[0], header=header, sep=sep,extra_geometry_columns=extra_geometry_columns)
        else:
            if profile_type == "timeseries":
                profile_dict = profile_timeseries(input_path=local_files[0], ts_mode_datetime_col=time_column, header=header, sep=sep, types_dict=types_dict)
            elif profile_type == "tabular":
                profile_dict = profile_tabular(input_path=local_files[0], header=header, sep=sep, extra_geometry_columns=extra_geometry_columns, types_dict=types_dict)
            elif profile_type == "textual":
                if len(files) == 1:
                    profile_dict = profile_text(my_path=local_files[0])
                else:
                    profile_dict = profile_text(my_path=local_files)
            elif profile_type == "raster":
                if len(files) == 1:
                    profile_dict = profile_raster(my_path=local_files[0])
                else:
                    profile_dict = profile_raster(my_path=local_files)
            elif profile_type == "rdfgraph":
                profile_dict = profile_tabular(input_path=local_files[0], header=header, sep=sep, extra_geometry_columns=extra_geometry_columns)
            elif profile_type == "hierarchical":
                profile_dict = profile_hierarchical(input_path=local_files[0])
            else:
                profile_dict = {}
        t = time() - t
        # output 
        
        if type_detection_mode:
            write_to_json(types_dict, "types_dict.json")
            if "types" in json_blob["output"]:
                mc.put_object(s3_path=json_blob["output"]["types"], file_path="types_dict.json")
        else:
            write_to_json(profile_dict, "profile.json")
            if "profile" in json_blob["output"]:
                mc.put_object(s3_path=json_blob["output"]["profile"], file_path="profile.json")
        
        # evaluate metrics
        metrics = {'time': t }
        
        return {
            "message": "stelardataprofiler Tool Executed Successfully",
            "output": json_blob["output"], 
            "metrics": metrics,
            "status": "success",
        }
        
        
    except Exception:
        print(traceback.format_exc())
        return {
            "message": "An error occurred during data processing.",
            "error": traceback.format_exc(),
            "status": 500
        }


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise ValueError("Please provide 2 files.")
    with open(sys.argv[1]) as o:
        j = json.load(o)
    response = run(j)
    with open(sys.argv[2], "w") as o:
        o.write(json.dumps(response, indent=4))
