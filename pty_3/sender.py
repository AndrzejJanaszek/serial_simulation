import os
import pty
import time
import threading
import serial
from structures import *
# from enum import Enum

def sender(tanks, DELAY, arduino_master_fd):
    simulation_time = 0

    # SIMULATION:
    while 1:
        # update values
        for tank in tanks:
            tank.fill_state = 0
            tank.dispense_state = 0
            if len(tank.fill_event_pool) > 0 and tank.fill_event_index < len(tank.fill_event_pool):
            # update event_index for both event types
                if simulation_time > tank.fill_event_pool[tank.fill_event_index].timeEnd:
                    tank.fill_event_index += 1
            
                # for FILL type --- update current_value and pin state
                if tank.fill_event_index < len(tank.fill_event_pool):
                    if simulation_time >= tank.fill_event_pool[tank.fill_event_index].timeStart and simulation_time <= tank.fill_event_pool[tank.fill_event_index].timeEnd:
                        tank.fill_state = 1
                        tank.current_value += tank.fill_event_pool[tank.fill_event_index].speedFactor * DELAY
            

            if len(tank.dispense_event_pool) > 0 and tank.dispense_event_index < len(tank.dispense_event_pool):
                if simulation_time > tank.dispense_event_pool[tank.dispense_event_index].timeEnd:
                    tank.dispense_event_index += 1

                # for DISPENSE type --- update current_value and pin state
                if tank.dispense_event_index < len(tank.dispense_event_pool):
                    if simulation_time >= tank.dispense_event_pool[tank.dispense_event_index].timeStart and simulation_time <= tank.dispense_event_pool[tank.dispense_event_index].timeEnd:
                        tank.dispense_state = 1
                        tank.current_value += tank.dispense_event_pool[tank.dispense_event_index].speedFactor * DELAY

            ### -------

            # send data
            w_s = f'{{"value":{tank.current_value}}}\n'
            os.write(tank.masted_fd, bytes(w_s, "utf-8"))
        

        # send arduino data
        arduino_json = "["

        for tank in tanks:
            f_str = '"{}":{},'.format(tank.pin_fill, tank.fill_state)
            d_str = '"{}":{},'.format(tank.pin_dispense, tank.dispense_state)
            arduino_json += f_str + d_str

        arduino_json += "]\n"

        os.write(arduino_master_fd, bytes(arduino_json, "utf-8"))

        simulation_time += DELAY
        time.sleep(DELAY)
