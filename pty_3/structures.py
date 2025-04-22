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