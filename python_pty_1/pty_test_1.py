import os
import pty
import time
import threading
import serial

def simulate_dosing(master_fd):
    time.sleep(1)
    os.write(master_fd, b'{"0": 1}\n')
    time.sleep(1)
    os.write(master_fd, b'{"0": 0}\n')
    time.sleep(2)
    os.write(master_fd, b'{"0": 1}\n')
    time.sleep(1)
    os.write(master_fd, b'{"0": 0}\n')

def run_main_program(slave_name):
    with serial.Serial(slave_name, 9600, timeout=10) as ser:
        while(1):
            ser.reset_input_buffer()
            print("Odebrano:", ser.readline().decode().strip())

master_fd, slave_fd = pty.openpty()
slave_name = os.ttyname(slave_fd)

# Start symulacji w osobnym wątku
threading.Thread(target=simulate_dosing, args=(master_fd,)).start()

# Uruchomienie programu głównego
run_main_program(slave_name)

