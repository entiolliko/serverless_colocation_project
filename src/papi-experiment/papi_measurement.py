import operator as op
import random
import sys
import uuid
import datetime 
import traceback
import gc
import speedtest
import json
import os
import numpy as np
import pypapi.exceptions
import requests


def start_benchmarking(disable_gc):
    if disable_gc:
        gc.disable()
    return datetime.datetime.now()

def stop_benchmarking():
    end = datetime.datetime.now()
    gc.enable()
    return end

def check_supported_events():
    from pypapi import papi_low as papi
    from pypapi import events as papi_events

    all_events = dir(papi_events)
    all_events = [event for event in all_events if (not event.startswith('_') and not event == "PAPI_END")]
    supported_events = []

    for event_name in all_events:
        papi.library_init()
        evs = papi.create_eventset()
        try:
            event_code = getattr(papi_events, event_name)
            papi.add_event(evs, event_code)
            supported_events.append(event_name)
        except Exception as e:
            papi.cleanup_eventset(evs)
            papi.destroy_eventset(evs)
            continue
            print(e)

        papi.cleanup_eventset(evs)
        papi.destroy_eventset(evs)

    return supported_events


class papi_benchmarker:
    from pypapi import papi_low as papi
    from pypapi import events as papi_events

    def __init__(self):
        self.events_names = []
        self.count = 0
        self.results = []
        self.papi.library_init()
        self.data = []     

    def measure_events(self, events_to_measure):
        self.events = self.papi.create_eventset()
        for event in events_to_measure:
            try:
                temp = getattr(self.papi_events, event)
                self.papi.add_event(self.events, temp)
                self.events_names += [event] 
                self.count += 1 
            except pypapi.exceptions.PapiInvalidValueError as err:
                print('Adding event {event} failed!'.format(event=event))
                continue
                # sys.exit(100)
            except pypapi.exceptions.PapiNoEventError as err:
                print('The event {event} does not exist.'.format(event=event))
                sys.exit(100)

    def start_overflow(self):
        self.papi.start(self.events)

    def stop_overflow(self):
        self.data += self.papi.stop(self.events)
        self.papi.cleanup_eventset(self.events)
        self.papi.destroy_eventset(self.events)

    def get_results(self):
        self.results = self.data

def measure_function(fun, config, cfg_path, papi_all_events): # fun pointer, fun config, papi config
    with open(cfg_path) as config_file:
       cfg = json.load(config_file)
    
    repetitions = cfg['benchmark']['repetitions']
    disable_gc = cfg['benchmark']['disable_gc']
    papi_experiments = papi_benchmarker()

    # print(papi_all_events)

    try:
        start = start_benchmarking(disable_gc)

        for start in range(0, len(papi_all_events), 2):
            end = min(len(papi_all_events), start + 2)
            papi_experiments.measure_events(papi_all_events[start:end])
            #for i in range(0, repetitions):
            papi_experiments.start_overflow()
            # Here you have to call the function with the input data from the config fiie 
            # res = function.handler(input_data)
            fun(config)
            papi_experiments.stop_overflow()
            # print(papi_experiments.data)

        end = stop_benchmarking()
    except Exception as e:
        print('Exception caught!')
        print(e)
        traceback.print_exc()

    papi_experiments.get_results()
    return papi_experiments.results
 

def workload(cfg):
    dtype = cfg["workload"]["element_type"]
    array_size = cfg["workload"]["array_size"]
    number_of_iterations = cfg["workload"]["iterations"]
    operator = cfg["workload"]["operator"]
    a = np.ones(array_size, dtype=dtype) * 2
    b = np.ones(array_size, dtype=dtype) * 3
    for _ in range(number_of_iterations):
        c = operator(a, b)


def allocate(cfg):
    size_in_bytes = cfg["memory"]["size_in_bytes"]
    arr = np.ones(int(size_in_bytes/4), dtype=np.dtype("int32"))


def test_disc(cfg):
    a = cfg["disc"]["a"] 
    file_name = cfg["disc"]["file_name"]
    np.save(file_name, a)
    with open('temp/temp_json.json') as json_data:
        d = json.load(json_data)


def fill_dict(dict_to_fill, cfg):
    number_of_entries = cfg["function_input"]["output_size"]
    for i in range(number_of_entries):
        dict_to_fill[str(uuid.uuid1())] = str(uuid.uuid1())


def test_write(cfg):
    file_name = cfg["writeFile"]["file_name"]
    a = cfg["writeFile"]["a"]
    np.save(file_name, a)


def network(cfg):
    use = cfg["network"]["use"]
    if use:
        url = ["https://pages.cs.wisc.edu/~remzi/OSTEP/cpu-intro.pdf", "https://pages.cs.wisc.edu/~remzi/OSTEP/vm-paging.pdf", 
               "https://pages.cs.wisc.edu/~remzi/OSTEP/threads-locks-usage.pdf", "https://pages.cs.wisc.edu/~remzi/OSTEP/file-journaling.pdf",
               "https://pages.cs.wisc.edu/~remzi/OSTEP/dialogue-vmm.pdf", "https://pages.cs.wisc.edu/~remzi/OSTEP/dialogue-vmm.pdf", "https://pages.cs.wisc.edu/~remzi/OSTEP/dialogue-vm.pdf"]
        directory = "temp"
        filename = None

        response = requests.get(url[random.randint(0, len(url) - 1)])
        response.raise_for_status()  # Check if the request was successful

        # file_path = os.path.join(directory, filename)
        # with open(file_path, 'wb') as file:
        #     file.write(response.content)


def create_parameters_workload(config, cfg):
    string_to_operator = {
    "+": op.add,
    "-": op.sub,
    "*": op.mul,
    "/": op.truediv,
    }
    cfg["workload"]["element_type"] = np.dtype(config.get("type", np.float32))
    cfg["workload"]["iterations"] = config.get("iterations")
    cfg["workload"]["array_size"] = int(config.get("array_size") / 4)
    cfg["workload"]["operator"] = string_to_operator[config.get("operator", "+")]


def create_parameters_memory(config, cfg):
    size_of_allocated_memory = config.get("size_in_bytes")
    cfg["memory"]["size_in_bytes"] = size_of_allocated_memory


def create_parameters_disc(config, cfg):
    block_size = config.get("block_size")
    file_name = config.get("path_to_file")
    a = np.ones(int(block_size // 4), dtype=np.dtype("int32")) * 2
    cfg["disc"]["a"] = a
    cfg["disc"]["file_name"] = file_name 


def create_parameters_function_input(config, cfg):
    number_of_entries = config.get("output_size")
    cfg["function_input"]["output_size"] = number_of_entries // 4


def create_parameters_writeFile(config, cfg):
    block_size = config.get("block_size", 0)
    cfg["writeFile"]["file_name"] = config.get("path_to_file", "temp_file.npy")
    cfg["writeFile"]["a"] = np.ones(int(block_size / 4), dtype=np.dtype("int32")) * 2


def create_parameters_network(config, cfg):
    use = config.get("use", False)
    cfg["network"]["use"] = use



def fill_function(cfg, config): # Config to fill, input config
    create_parameters_writeFile(config["writeFile"], cfg)

    create_parameters_disc(config["disc"], cfg)

    create_parameters_function_input(config["function_input"], cfg)

    create_parameters_memory(config["memory"], cfg)

    create_parameters_workload(config["workload"], cfg)
    
    create_parameters_network(config["network"], cfg)


def microbenchmark_sample_run(cfg):
    test_write(cfg)
    test_disc(cfg)
    result = {}
    fill_dict(result, cfg)
    allocate(cfg)
    workload(cfg)
    network(cfg)

def papi_handler(input_config):
    papi_all_events = input_config[1]
    input_config = input_config[0]
    result = []

    cfg = {"workload": {}, "function_input" : {}, "readFile": {}, "disc": {}, "writeFile": {}, "memory": {}, "network": {}}
    fill_function(cfg, input_config["config"])
    result = measure_function(microbenchmark_sample_run, cfg, "src/papi-experiment/configs/papi_config.json", papi_all_events)

    return {"ID": input_config["ID"], "res": result}	

def sample_run_handler(input_config):
    cfg = {"workload": {}, "function_input" : {}, "readFile": {}, "disc": {}, "writeFile": {}, "memory": {}, "network": {}}
    fill_function(cfg, input_config["config"])
    microbenchmark_sample_run(cfg)

