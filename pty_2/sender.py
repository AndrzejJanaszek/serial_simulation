import os
import pty
import time
import threading
import serial
import enum

class EventType(enum):
    DISPENSE = 1
    FILL = 2

class EventPoolObject:
    def __init__(self, timeStart, timeEnd, eventType : EventType, speedFactor):
        self.timeStart = timeStart
        self.timeEnd = timeEnd
        self.eventType : EventType = eventType
        self.speedFactor = speedFactor

def complex_sender(arduino_master_fd, weight_master_fd):
    event_pool = [
        EventPoolObject(1, 3, EventType.DISPENSE, 100)
    ]

    event_index = 0
    simTime = 0
    delay = 0.1

    currentValue = 1000

    while 1:
        if simTime > event_pool[event_index].timeEnd:
            event_index += 1

        if event_index >= len(event_pool):
            print("Koniec event pool")
            break

        if sTime >= event_pool[event_index].timeStart and sTime <= event_pool[event_index].timeEnd:
            if event_pool[event_index].eventType == EventType.DISPENSE:     
                currentValue -= event_pool[event_index].speedFactor*delay
            else:
                currentValue += event_pool[event_index].speedFactor*delay
            
            os.write(master_fd, b'{"0":1}\n', "utf-8")
        else:
            os.write(master_fd, b'{"0":10}\n', "utf-8")


        


        sTime += delay
        time.sleep(delay)




def arduino_sender(master_fd):
    # time at which state must change
    event_index = 0
    event_pool = [1,3]
    sTime = 0 # simulationTime
    pinState = 0

    delay = 0.1

    while(1):
        if event_index >= len(event_pool):
            print("Koniec event pool")
            break

        if sTime >= event_pool[event_index]:
            pinState = not pinState
            event_index += 1

        s = f'{{"0":{pinState}}}\n'
        os.write(master_fd, bytes(s, "utf-8"))

        sTime += delay
        time.sleep(delay)

def weight_sender(master_fd):
    event_index = 0
    event_pool_time = [{"start":1,"end":3}]

    currentValue = 700

    sTime = 0 # simulationTime

    speedFactor = 100
    delay = 0.1

    while(1):
        if sTime > event_pool_time[event_index]["end"]:
            event_index += 1

        if event_index >= len(event_pool_time):
            print("Koniec event pool")
            break

        if sTime >= event_pool_time[event_index]["start"] and sTime <= event_pool_time[event_index]["end"]:
            currentValue -= speedFactor*delay

        s = f'{currentValue}\n'
        os.write(master_fd, bytes(s, "utf-8"))

        sTime += delay
        time.sleep(delay)

    time.sleep(0.1)

def run_main_program(slave_name):
    with serial.Serial(slave_name, 9600, timeout=1) as ser:
        while(1):
            ser.reset_input_buffer()
            print("Odebrano:", ser.readline().decode().strip())

master_fd, slave_fd = pty.openpty()
slave_name = os.ttyname(slave_fd)

# Start symulacji w osobnym wątku
threading.Thread(target=weight_sender, args=(master_fd,)).start()

# Uruchomienie programu głównego
run_main_program(slave_name)
