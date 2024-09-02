import sys
import json
import code_composer
import requirements_composer
import input_composer
import random
import os
import datetime
import numpy
from scipy.stats import burr
from function_generator import generate_function_from_config

C = 11.652
D = 0.221
SCALE = 107.083
NUMBER_OF_DATAPOINTS = 250 
possible_values = list(range(100000, 1100001, 100000))
operators = ["+", "-", "*", "/"]

def generate_configs(path_to_file, folder_name):
    config = {"writeFile": {}, "disc": {}, "function_input": {}, "memory": {}, "workload": {}, "network": {}}
    total_memory_usage = burr.rvs(C, D, SCALE, 1) 
    config["writeFile"]["path_to_file"] = path_to_file
    config["disc"]["path_to_file"] = path_to_file

    counter = 0
    while counter < NUMBER_OF_DATAPOINTS:
        memory_use = int(burr.rvs(C, D, SCALE, size=2)[0] / 5)
        network_use = random.choice([True, False])
        workload_iterations = random.choice(possible_values)
        workload_operator  = random.choice(operators)

        config["disc"]["block_size"] = memory_use 
        config["function_input"]["output_size"] = memory_use
        config["memory"]["size_in_bytes"] = memory_use
        config["workload"]["array_size"] = memory_use 
        config["writeFile"]["block_size"] = memory_use
        config["workload"]["type"] = "float32"
        config["network"]["use"] = False 
        config["workload"]["iterations"] = workload_iterations
        config["workload"]["operator"] = workload_operator
                    
        generate_function_from_config(config, folder_name, counter)
        counter += 1
                                
if __name__ == "__main__":
    path_to_file = "temp/temp_file.npy"
    generate_configs(path_to_file, sys.argv[1])
