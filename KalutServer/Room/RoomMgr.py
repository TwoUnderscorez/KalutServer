from KalutServer.Exceptions import *
import KalutServer.conf as myconf
from KalutServer.Room import Room
from random import randint
import threading
import time
import Queue
import select
import socket
import sys
import json
import traceback
rooms = dict()

def soc_router():
    srvsoc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srvsoc.bind((myconf.host, myconf.sock_port))
    srvsoc.listen(5)
    while 1:
        cltsock, addr = srvsoc.accept()
        data = cltsock.recv(1024)
        print 'routing client...'
        try:
            if data:
                req = json.loads(data)
                if int(req['pin']) in rooms.keys() and req['name']:
                    if rooms[req['pin']].status in ('WAITING_FOR_PLAYERS', 'WAITING_FOR_LAST_PLAYER'):
                        cltsock.send(json.dumps({'status' : 'ok', 'UID' : str(rooms[req['pin']].game_uid)}))
                        rooms[req['pin']].add_client(cltsock, req['name'])
                        if not rooms[req['pin']].running:
                            t = threading.Thread(target=start_room, args=(req['pin'],))
                            t.start()
                    else:
                        cltsock.send(json.dumps({'status' : "Room isn't waiting for players."}))
                        cltsock.close()
                else:
                    cltsock.send(json.dumps({'status' : 'invalid pin.'}))
                    cltsock.close()
            else:
                cltsock.close()
        except:
            print traceback.format_exc()
            cltsock.close()

def start_room(pin):
    room = rooms[pin]
    room.running = True
    print 'starting room pin=' + str(pin)
    room.mainloop()

def start_room_async(pin):
    t = threading.Thread(target=start_room, args=(pin,))
    t.start()

def create_room(uid, pin=0):
    while pin in rooms.keys() or pin==0:
        pin=randint(1000,10000) 
    rooms[pin]=Room.Room(pin, uid)
    print 'created room + pin=' + str(pin)
    return pin

def close_room(pin):
    if pin in rooms.keys():
        rooms[pin].close()
        del rooms[pin]