# import KalutServer.Model.Communicator as cm
from KalutServer.Exceptions import *
import Queue
import select
import socket
import sys
import time
import json
import threading

class Room(object):
    def __init__(self, pin, game_uid):
        self.status='WAITING_FOR_PLAYERS'
        self.pin = pin
        self.game_uid = game_uid
        self.inputs = []
        self.outputs = []
        self.message_queues = dict() # sock : Queue
        self.running = False
        self.clients = dict() # sock : [name, points]
        self.select_lock = threading.Lock()
    
    def add_client(self, connection, name):
        connection.setblocking(0)
        self.select_lock.acquire()
        self.inputs.append(connection)
        self.message_queues[connection] = Queue.Queue()
        if name == '@#@WALLVIEW@#@':
            self.clients[connection]=[name, -1]
        else:
            self.clients[connection]=[name, 0]
        self.select_lock.release()
        print 'client connected'

    def handle_request(self, data):
        req = json.loads(data)
        if req['request']:
            func = req['request']
            args = req["args"]
            return json.dumps(getattr(self, func)(*args))

    def get_players(self):
        res = dict()
        res['players'] = []
        self.select_lock.acquire()
        for key in self.clients.values():
            if key[1]>-1:
                res['players'].append(key[0])
        self.select_lock.release()
        return res

    def mainloop(self):
        while self.running:
            Queue.Queue().get
            if not self.inputs:
                time.sleep(0.5)
                continue

            time.sleep(0.2)
            self.select_lock.acquire()
            self.readable, self.writable, self.exceptional = select.select(
                self.inputs, self.outputs, self.inputs)
            self.select_lock.release()

            for s in self.readable:
                data = s.recv(1024)
                if data:
                    tosend = self.handle_request(data)
                    if tosend:
                        self.message_queues[s].put(tosend)
                    if s not in self.outputs:
                        self.outputs.append(s)
                else:
                    if s in self.outputs:
                        self.outputs.remove(s)
                    self.inputs.remove(s)
                    s.close()
                    del self.message_queues[s]
                    del self.clients[s]

            for s in self.writable:
                try:
                    next_msg = self.message_queues[s].get_nowait()
                except Queue.Empty:
                    self.outputs.remove(s)
                else:
                    s.send(next_msg)

            for s in self.exceptional:
                self.inputs.remove(s)
                if s in self.outputs:
                    self.outputs.remove(s)
                s.close()
                del self.message_queues[s]
                del self.clients[s]


    def close(self):
        pass