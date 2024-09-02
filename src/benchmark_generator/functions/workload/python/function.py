#test
config = {
    "iterations": 1000000,
    "operator": "-",
    "type": "float32",
    "array_size": 10000
}
cfg = {}
#import
import numpy as np
import time
import operator as op
#parameter_fun
def create_parameters_workload(config, cfg):
    string_to_operator = {
    "+": op.add,
    "-": op.sub,
    "*": op.mul,
    "/": op.truediv,
    }
    cfg["workload"]["element_type"] = np.dtype(config.get("type", np.float32))
    cfg["workload"]["iterations"] = config.get("iterations")
    cfg["workload"]["array_size"] = config.get("array_size")
    cfg["workload"]["operator"] = string_to_operator[config.get("operator", "+")]
#function
def workload(cfg):
    dtype = cfg["workload"]["element_type"]
    array_size = cfg["workload"]["array_size"]
    number_of_iterations = cfg["workload"]["iterations"]
    operator = cfg["workload"]["operator"]
    a = np.ones(array_size, dtype=dtype) * 2
    b = np.ones(array_size, dtype=dtype) * 3
    for i in range(number_of_iterations):
        c = operator(a, b)
#create_cfg
create_parameters_workload(config, cfg)
#run
workload(cfg)
