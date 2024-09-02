import random
import sys
import json
from pypapi import papi_low as papi
from pypapi import events as papi_events

def check_supported_events():
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

   #with open(sys.argv[1], 'r') as file:
   #    data = json.load(file)

#  #  random.shuffle(supported_events)
   #data["benchmark"]["papi"]["events"] = supported_events

   #with open(sys.argv[1], 'w') as file:
   #    json.dump(data, file)

    return supported_events

if __name__ == '__main__':
    supported_events = check_supported_events()
    print("Supported PAPI events:")
    for event in supported_events:
        print(event)
