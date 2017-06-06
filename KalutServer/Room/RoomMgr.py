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
import ssl
rooms = dict()
srvsoc = socket.socket()

def soc_router():
    global srvsoc
    srvsoc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srvsoc.bind((myconf.host, myconf.sock_port))
    srvsoc.listen(5)
    while 1:
        try:
            sslcltsock, addr = srvsoc.accept()
            # sslcltsock = ssl.wrap_socket(cltsock, myconf.keyfile, myconf.certfile, server_side=True)
            data = sslcltsock.recv(1024)
        except:
            print 'Server socket closed.'
            break
        try:
            if data:
                req = json.loads(data)
                rint 'Client with name {0} connected, client...'.format(req['name'])
                if int(req['pin']) in rooms.keys() and req['name']:
                    if rooms[req['pin']].status in ('WAITING_FOR_PLAYERS', 'WAITING_FOR_LAST_PLAYER'):
                        sslcltsock.send(json.dumps({'status' : 'ok', 'UID' : str(rooms[req['pin']].game_uid)}))
                        rooms[req['pin']].add_client(sslcltsock, req['name'])
                        if not rooms[req['pin']].running:
                            t = threading.Thread(target=start_room, args=(req['pin'],))
                            t.start()
                    else:
                        sslcltsock.send(json.dumps({'status' : "Room isn't waiting for players."}))
                        sslcltsock.close()
                else:
                    sslcltsock.send(json.dumps({'status' : 'invalid pin.'}))
                    sslcltsock.close()
            else:
                sslcltsock.close()
        except:
            sslcltsock.close()
            print traceback.format_exc()
            break

def start_room(pin):
    room = rooms[pin]
    room.running = True
    print 'starting room with pin of ' + str(pin)
    room.mainloop()

def close_srvsoc():
    global srvsoc
    srvsoc.close()

def are_there_rooms_running():
    '''Returns true of there are no running rooms.'''
    return len(rooms.keys())==0

def start_room_async(pin):
    t = threading.Thread(target=start_room, args=(pin,))
    t.start()

def create_room(uid, pin=0):
    while pin in rooms.keys() or pin==0:
        pin=randint(1000,10000) 
    rooms[pin]=Room.Room(pin, uid)
    print 'created room with pin of' + str(pin)
    return pin

def close_room(pin):
    if pin in rooms.keys():
        del rooms[pin]

def close_all_rooms():
    global srvsoc
    for pin, room in rooms.items():
        room.close()
    s = socket.socket()
    s.connect((myconf.host, myconf.sock_port))
    srvsoc.close()
    s.close()
