from KalutServer.Model.Communicator import Communicator
from KalutServer.RESTfulAPI.server import start_server
from KalutServer.Exceptions import *
from KalutServer.Room import Room
from KalutServer.Room.RoomMgr import soc_router
from random import randint
import threading
import time
import Queue
import select
import socket
import sys
import json

#### ENTRY POINT ####
def RunKalutServer():
    global rooms
    # RESTful API
    print 'Initializing RESTful API...'
    RESTfulAPI_thread = threading.Thread(target=RESTfulAPI_main, name='RESTfulAPI_thread')
    RESTfulAPI_thread.daemon = True
    RESTfulAPI_thread.start()

    soc_router()

def RESTfulAPI_main():
    start_server()       

if __name__=='__main__':
    pass