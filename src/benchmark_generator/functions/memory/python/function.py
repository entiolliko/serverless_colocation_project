#test
config = {
    "size_in_bytes": 1024 * 1024
}
result = {}
cfg = {}
number = 0
#import
import numpy as np
import time
#parameter_fun
def create_parameters_memory(config, cfg):
    size_of_allocated_memory = config.get("size_in_bytes")
    cfg["memory"]["size_in_bytes"] = size_of_allocated_memory
#function
def allocate(cfg):
    size_in_bytes = cfg["memory"]["size_in_bytes"]
    arr = np.ones(int(size_in_bytes/4), dtype=np.dtype("int32"))
#create_cfg
create_parameters_memory(config, cfg)
#run
allocate(cfg)
