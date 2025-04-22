import config
import serial
import time

def reader():
    with serial.Serial(config.arduino_slave_name, 9600, timeout=1) as a_ser:
        while(1):
            a_ser.reset_input_buffer()
            print("[A]: Odebrano:", a_ser.readline().decode().strip())
            time.sleep(.1)
    # and for each serial name in: (config.tanks)
    #     tanks=[
    # "/dev/pts/5",
    # "/dev/pts/6",
    # "/dev/pts/7",
    # "/dev/pts/8",
    # ]

import config
import serial
import threading
import time

def read_serial(name, label):
    try:
        with serial.Serial(name, 9600, timeout=1) as ser:
            while True:
                ser.reset_input_buffer()
                line = ser.readline().decode().strip()
                if line:
                    print(f"[{label}]: {line}")
                time.sleep(0.1)
    except Exception as e:
        print(f"[{label}] Błąd: {e}")

def reader():
    # Wątek dla Arduino master
    threading.Thread(target=read_serial, args=(config.arduino_slave_name, "A"), daemon=True).start()

    # Wątki dla tanków
    for i, tank in enumerate(config.tanks):
        pre = "\t"*(3*i)
        threading.Thread(target=read_serial, args=(tank, pre+f"T{i}"), daemon=True).start()

    # Trzymaj program aktywny
    while True:
        time.sleep(1)
