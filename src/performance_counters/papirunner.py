import time
import datetime, json, sys, traceback, csv, random
from utils import *
from tools import *
import os
import pypapi.exceptions

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

def measure_function(fun, config, cfg_path):
    with open(cfg_path) as config_file:
        cfg = json.load(config_file)

    repetitions = cfg['benchmark']['repetitions']
    disable_gc = cfg['benchmark']['disable_gc']
    papi_experiments = papi_benchmarker()
    papi_all_events = cfg['benchmark']['papi']["events"] 
    timedata = [0] * repetitions
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
    result_path = "src/performance_counters/results/" + cfg['benchmark']["name"] + ".csv" 

    first_line = ""
    if not os.path.exists(result_path):
        with open(result_path, 'w') as f:
            f.write('')

    with open(result_path, 'r') as f:
        first_line = f.readline()

    with open(result_path, 'a') as f:
        csv_writer = csv.writer(f)
        if first_line == "":
            csv_writer.writerow(papi_experiments.events_names)
        csv_writer.writerow(papi_experiments.results)
    
