import KalutServer.Model.Communicator
from KalutServer.Exceptions import *
import KalutServer.Room.RoomMgr
import Queue
import select
import socket
import sys
import time
import json
import threading
import time
import ssl


class Room(object):
    def __init__(self, pin, game_uid):
        self.status='WAITING_FOR_PLAYERS'
        self.pin = pin
        self.game_uid = game_uid
        self.game_data = None
        self.game_desc = None
        self.inputs = []
        self.outputs = []
        self.message_queues = dict() # sock : Queue
        self.running = False
        self.clients = dict() # sock : [name, points]
        self.select_lock = threading.Lock()
        self.load_game_data()
        self.time_to_remember = time.time()
        self.event_register = [] # soc
        self.on_question = 0
        self.wallview_pressed_next = False
        self.correct_ans_index = []
    
    def load_game_data(self):
        cmm = KalutServer.Model.Communicator.Communicator()
        self.game_data = json.loads(cmm.get_quiz_data(self.game_uid)['Quiz'])
        self.game_desc = cmm.get_quiz_info(self.game_uid)
        cmm.logout()

    def add_client(self, connection, name):
        connection.setblocking(0)
        self.select_lock.acquire()
        self.inputs.append(connection)
        self.message_queues[connection] = Queue.Queue()
        if name == '@#@WALLVIEW@#@':
            self.clients[connection]=[name, -1]
        else:
            if len(self.clients) < 2:
                self.time_to_remember = time.time()
            self.clients[connection]=[name, 0]
        self.select_lock.release()
        print '{0} connected to room {1}'.format(self.clients[s][0], self.pin)
        
    def answer(self, s, ans, t):
        if int(ans) in self.correct_ans_index:
            time_left = t - self.time_to_remember
            if time_left < 1:
                time_left = 1
            self.clients[s][1] += int(100 * self.game_data[self.on_question - 1]["Time"]/time_left)
            return {'Points' : str(self.clients[s][1]), 'Correct' : str(True)}
        else:
            return {'Points' : str(self.clients[s][1]), 'Correct' : str(False)}
        

    def wallview_next_q(self, s):
        if self.status == 'WAITING_FOR_PLAYERS':
            if len(self.clients) > 2:
                self.status = 'WAITING_FOR_LAST_PLAYER'
                return {'status' : 'ok'}
            else:
                return {'status' : 'err', 'msg' : 'There arn\'t enough players to start a game.'}
        else:
            self.wallview_pressed_next = True
            return {'status' : 'ok'}

    def handle_request(self, data, s):
        req = json.loads(data)
        if req['request']:
            func = req['request']
            args = req["args"]
            retdata = getattr(self, func)(s, *args)
            if retdata:
                return json.dumps(retdata)
            else:
                return False

    def register_event(self, s):
        self.event_register.append(s)
        return None

    def trigger_event(self, data):
        for s in self.event_register:
            if s in self.message_queues:
                self.message_queues[s].put(json.dumps(data))
                self.outputs.append(s)
        self.event_register = []

    def get_players(self, s):
        res = dict()
        res['players'] = []
        self.select_lock.acquire()
        for key in self.clients.values():
            if key[1]>-1:
                res['players'].append(key[0])
        self.select_lock.release()
        res['players']=json.dumps(res['players'])
        res['game_status']=self.status
        res['trigglen']=str(len(self.event_register))
        res['onq']=str(self.on_question - 1)
        if self.status in ('END_OF_GAME', 'GAME_ENDED'):
            res['status']='eog'
        return res

    def update_correct_ans_index(self):
        self.correct_ans_index = []
        for qitem in range(0, len(self.game_data[self.on_question - 1]["Answers"]) ):
            if self.game_data[self.on_question - 1]["Answers"][qitem]["Value"]:
                self.correct_ans_index.append(qitem)

    def handle_game_status_and_events(self):
        if self.status == 'WAITING_FOR_PLAYERS':
            override = int(self.game_desc["Timeout"])==0
            if int(self.game_desc["Timeout"])!=0 and \
                (time.time() - self.time_to_remember > int(self.game_desc["Timeout"])):
                if len(self.clients) > 2 and len(self.event_register) > 1:
                    self.status = 'NextQ'
                elif len(self.clients) > 1:
                    self.status = 'WAITING_FOR_LAST_PLAYER'
        elif self.status == 'WAITING_FOR_LAST_PLAYER':
            if len(self.clients) > 2:
                self.status = 'WAITING_FOR_LAST_PLAYER_SYNC'
        elif self.status == 'WAITING_FOR_LAST_PLAYER_SYNC':
            if len(self.event_register) > 1:
                self.status = 'NextQ'
        elif self.status == 'NextQ':
            self.on_question+=1
            if self.on_question > len(self.game_data):
                self.status = 'END_OF_GAME'
                return
            self.update_correct_ans_index()
            self.time_to_remember = time.time()
            self.trigger_event({'ShowQ' : str(self.on_question - 1), 'status' : 'ok'})
            self.status = 'WAIT_FOR_Q_TIMEOUT'
            self.wallview_pressed_next = False
        elif self.status == 'WAIT_FOR_Q_TIMEOUT':
            if (len(self.clients) == len(self.event_register) + 1) and self.wallview_pressed_next:
                self.status = 'NextQ'
        elif self.status == 'END_OF_GAME':
            self.end_game()
            self.status = 'GAME_ENDED'
        elif self.status == 'GAME_ENDED':
            if len(self.clients)==0:
                self.running=False
            print 'Room {0} exited'.format(self.pin)
    def end_game(self):
        maxx=0
        maxxname=''
        for s,keydata in self.clients.items():
            if keydata[1]>maxx:
                maxx=keydata[1]
                maxxname=keydata[0]
        self.trigger_event({'status' : 'eog', 'winner' : '{0} won with {1} points.'.format(maxxname, maxx)})
        

    def mainloop(self):
        while self.running:
            self.handle_game_status_and_events()      
                
            if not self.inputs:
                time.sleep(0.5)
                continue
            
            if len(self.clients) < 3 and len(self.event_register) > 0 and self.status not in ('WAITING_FOR_PLAYERS', 'WAITING_FOR_LAST_PLAYER'):
                self.status = 'END_OF_GAME'

            self.select_lock.acquire()
            try:
                self.readable, self.writable, self.exceptional = select.select(
                    self.inputs, self.outputs, self.inputs)
            except:
                self.running=False
            self.select_lock.release()

            for s in self.readable:
                try:
                    data = s.recv(1024)
                except:
                    data = None
                if data:
                    tosend = self.handle_request(data, s)
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
                    if s in self.outputs:
                        self.outputs.remove(s)
                except KeyError:
                    pass
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
        self.running = False
        for s,pin in self.clients.items():
            s.close()