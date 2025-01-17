#!/usr/bin/env python

__author__ = "David Hayward"
__copyrights__ = "Copyright 2019, the python-uds project"
__credits__ = ["David Hayward"]

__license__ = "MIT"
__maintainer__ = "Richard Clubb"
__email__ = "richard.clubb@embeduk.com"
__status__ = "Development"


import can
from uds import fillArray

##
# @class CanListener
# @brief This is used due to new implementation of python-can 4.0.0 version
#
# Just create a Listener inherit from can.listener(abstract class) and 
# define the needed method on_message_received
class CanListener(can.Listener):

    def __init__(self):
        super().__init__()

    ##
    # @brief just avoid abstract class error, this class will be override
    # by callback parameter from CanConnection constructor
    def on_message_received(self):
        pass
##
# @brief Small class to wrap the CAN Bus/Notifier/Listeners to allow multiple clients for each bus/connection
class CanConnection(object):

    def __init__(self, callback, filter, bus, is_external=False):
        self.__bus = bus
        self.__is_external = is_external
        if not self.__is_external:
            listener = CanListener()
            listener.on_message_received = callback
            self.__notifier = can.Notifier(self.__bus, [listener], 1.0)
            self.__listeners = [listener]
            self.addFilter(filter)

    ##
    # @brief Adds call back (via additional listener) to the notifier which is attached to this bus
    def addCallback(self, callback):
        listener = CanListener()
        listener.on_message_received = callback
        self.__notifier.add_listener(listener)
        self.__listeners.append(listener)

    ##
    # @brief Adds a filter (CAN Msg Id) to the bus to allow messages through to the callback
    def addFilter(self, filter):
        filters = self.__bus.filters
        if filters is not None:
            filters.append({"can_id": filter, "can_mask": 0xFFF, "extended": False})
        else:
            filters = [{"can_id": filter, "can_mask": 0xFFF, "extended": False}]
        self.__bus.set_filters(filters)

    ##
    # @brief transmits the data over can using can connection
    def transmit(self, data, reqId, extended=False):
        canMsg = can.Message(arbitration_id=reqId, is_extended_id=extended)
        canMsg.dlc = len(data)
        
        canMsg.data = data
        canMsg.is_fd = True

        self.__bus.send(canMsg)

    def shutdown(self):
        if self.__is_external == False:
            self.__notifier.stop()
            self.__bus.reset()
            self.__bus.shutdown()
            self.__bus = None
    
    def get_bus(self):
        return self.__bus
