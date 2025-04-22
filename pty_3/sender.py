import os
import pty
import time
import threading
import serial
from enum import Enum

class EventType(Enum):
    DISPENSE = 1
    FILL = 2

class EventPoolObject:
    def __init__(self, timeStart, timeEnd, eventType : EventType, speedFactor):
        self.timeStart = timeStart
        self.timeEnd = timeEnd
        self.eventType : EventType = eventType
        self.speedFactor = speedFactor

class TestTank:
    def __init__(self, pin_fill, pin_dispense, current_value):
        self.pin_fill = pin_fill
        self.pin_dispense = pin_dispense
        self.current_value = current_value
        
        self.fill_event_pool = []
        self.dispense_event_pool = []
        
        self.fill_event_index = 0
        self.dispense_event_index = 0
        self.fill_state = 0
        self.dispense_state = 0

        self.masted_fd = None
        self.slave_name = None
        
    
    def add_fill_event(self, event : EventPoolObject):
        self.fill_event_pool.append(event)

    def add_dispense_event(self, event : EventPoolObject):
        self.dispense_event_pool.append(event)

    def set_master_slave(self, master, slave):
        self.masted_fd = master
        self.slave_name = slave

def manager():
    # setup
    tanks = [
        TestTank(pin_fill=0, pin_dispense=1, current_value=10000)
    ]

    DELAY = 0.1
    simulation_time = 0

    # fake ports
    arduino_master_fd, arduino_slave_fd = pty.openpty()
    arduino_slave_name = os.ttyname(arduino_slave_fd)

    for tank in tanks:
        master_fd, slave_fd = pty.openpty()
        slave_name = os.ttyname(slave_fd)

        tank.set_master_slave(master=master_fd, slave=slave_name)


    # SIMULATION:
    while 1:
        # update values
        for tank in tanks:
            # update event_index for both event types
            if simulation_time > tank.fill_event_pool[tank.fill_event_index].timeEnd:
                tank.fill_event_index += 1
            if simulation_time > tank.dispense_event_pool[tank.dispense_event_index].timeEnd:
                tank.dispense_event_index += 1


            # for FILL type --- update current_value and pin state
            if tank.fill_event_index < len(tank.fill_event_pool):
                tank.fill_state = 0
                if simulation_time >= tank.fill_event_pool[tank.fill_event_index].timeStart and simulation_time <= tank.fill_event_pool[tank.fill_event_index].timeEnd:
                    tank.fill_state = 1
                    tank.current_value += tank.fill_event_pool[tank.fill_event_index].speedFactor * DELAY

            # for DISPENSE type --- update current_value and pin state
            if tank.dispense_event_index < len(tank.dispense_event_pool):
                tank.dispense_state = 0
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
            f_str = '\n"{}":{},\n'.format(tank.pin_fill, tank.fill_state)
            d_str = '"{}":{},'.format(tank.pin_dispense, tank.dispense_state)
            arduino_json += f_str + d_str

        arduino_json[-1] = "]"

        os.write(arduino_master_fd, bytes(arduino_json, "utf-8"))

        simulation_time += DELAY
        time.sleep(DELAY)

def complex_sender(arduino_master_fd, weight_master_fd):
    event_pool = [
        EventPoolObject(1, 3, EventType.DISPENSE, -100)
    ]

    # settup
    delay = 0.1
    event_index = 0
    sTime = 0
    pinState = 0

    currentValue = 1000

    while 1:
        if sTime > event_pool[event_index].timeEnd:
            event_index += 1

        if event_index >= len(event_pool):
            print("Koniec event pool")
            break

        #   set pinState and currentValue depending on currentEvent
        pinState = 0
        if sTime >= event_pool[event_index].timeStart and sTime <= event_pool[event_index].timeEnd:
            pinState = 1
            # if despense -> speedFactor < 0
            currentValue += event_pool[event_index].speedFactor*delay

        
        #   send serial
        a_s = f'{{"0":{pinState}}}\n'
        os.write(arduino_master_fd, bytes(a_s, "utf-8"))
        w_s = f'{{"value":{currentValue}}}\n'
        os.write(weight_master_fd, bytes(w_s, "utf-8"))

        sTime += delay
        time.sleep(delay)


def read_arduino(arduino_slave_name):
    print(arduino_slave_name)
    with serial.Serial(arduino_slave_name, 9600, timeout=1) as a_ser:
    #   end with w_ser for weight_slave_name
        while(1):
            a_ser.reset_input_buffer()
            print("[A]: Odebrano:", a_ser.readline().decode().strip())
            time.sleep(.6)


def read_weights(weight_slave_name):
    with serial.Serial(weight_slave_name, 9600, timeout=1) as a_ser:
        while(1):
            a_ser.reset_input_buffer()
            print("\t\t\t[W]: Odebrano:", a_ser.readline().decode().strip())
            time.sleep(.6)


arduino_master_fd, arduino_slave_fd = pty.openpty()
arduino_slave_name = os.ttyname(arduino_slave_fd)

weight_master_fd, weight_slave_fd = pty.openpty()
weight_slave_name = os.ttyname(weight_slave_fd)


threading.Thread(target=complex_sender, args=(arduino_master_fd,weight_master_fd)).start()
threading.Thread(target=read_arduino, args=(arduino_slave_name, )).start()
threading.Thread(target=read_weights, args=(weight_slave_name, )).start()
# threading.Thread(target=weight_sender, args=(weight_master_fd,)).start()

# Uruchomienie programu głównego
# read_arduino(arduino_slave_name)
