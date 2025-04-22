import os
import pty
import time
import threading
import serial
from enum import Enum
from structures import *
from sender import sender
from reader import reader


# setup
tanks = [
    TestTank(pin_fill=0, pin_dispense=1, current_value=10000),
    TestTank(pin_fill=2, pin_dispense=3, current_value=20000),
    TestTank(pin_fill=4, pin_dispense=5, current_value=30000),
    TestTank(pin_fill=6, pin_dispense=7, current_value=40000)
]
tanks[0].add_fill_event( EventPoolObject(1, 3, EventType.DISPENSE, 100) )
DELAY = 0.1

arduino_master_fd, arduino_slave_fd = pty.openpty()
arduino_slave_name = os.ttyname(arduino_slave_fd)

for tank in tanks:
    master_fd, slave_fd = pty.openpty()
    slave_name = os.ttyname(slave_fd)

    tank.set_master_slave(master=master_fd, slave=slave_name)


# save configuration
current_dir = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(current_dir, "config.py")

with open(file_path, "w") as f:
    a_config = 'arduino_slave_name="' + arduino_slave_name + '"\n'
    f.write(a_config)

    t_config = "tanks=[\n"
    for tank in tanks:
        t_config += '"'+tank.slave_name + '",\n'
    t_config += "]\n"

    f.write(t_config)



# run sender
# sender(tanks=tanks, DELAY=DELAY)
threading.Thread(target=sender, args=(tanks, DELAY, arduino_master_fd)).start()
threading.Thread(target=reader).start()