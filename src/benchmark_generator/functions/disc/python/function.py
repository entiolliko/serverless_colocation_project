#test
config = {
    "block_size": 1024*1024*128,
    "path_to_file": "temp_file.npy"
}
cfg = {}
number = 0
#import
import numpy as np
import time
import uuid
import os
#parameter_fun
def create_parameters_disc(config, cfg):
    block_size = config.get("block_size")
    file_name = config.get("path_to_file")
    a = np.ones(int(block_size / 4), dtype=np.dtype("int32")) * 2
    cfg["disc"]["a"] = a
    cfg["disc"]["file_name"] = file_name 
#function
def test_disc(cfg):
    a = cfg["disc"]["a"] 
    file_name = cfg["disc"]["file_name"]
    np.save(file_name, a)
    np.load(file_name)
#create_cfg
create_parameters_disc(config, cfg)
#run
test_disc(cfg)
