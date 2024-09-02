#test
config = {
    "path_to_file": "temp_file.npy",
    "block_size": 1024*1024*128
}
cfg = {}
#import
import numpy as np
import time
import uuid
import os
#parameter_fun
def create_parameters_writeFile(config, cfg):
    block_size = config.get("block_size", 0)
    cfg["writeFile"]["file_name"] = config.get("path_to_file", "temp_file.npy")
    cfg["writeFile"]["a"] = np.ones(int(block_size / 4), dtype=np.dtype("int32")) * 2
#function
def test_write(cfg):
    file_name = cfg["writeFile"]["file_name"]
    a = cfg["writeFile"]["a"]
    np.save(file_name, a)
#create_cfg
create_parameters_writeFile(config, cfg)
#run
test_write(cfg)

