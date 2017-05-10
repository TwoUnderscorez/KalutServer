import SSLbottle as blt
from KalutServer.Model.Communicator import Communicator 
import json

@blt.get('/')
def test():
    return 'OK'

def handle_cm_func(func, *args):
    model = Communicator()
    data = func(model, *args)
    model.logout()
    return data

def start_server():
    srv = blt.SSLWSGIRefServer(host="192.168.1.160", port=25565)
    blt.run(server=srv)

### /quizes
@blt.get('/quizes/get_quiz_info_by_uid&<uid>')
def get_quiz_info_by_uid(uid):
    return handle_cm_func(Communicator.get_quiz_info, uid)

@blt.get('/quizes/get_all_quizes_info')
def get_all_quizes_info():
    return dict(handle_cm_func(Communicator.get_all_quizes_info))

@blt.get('/quizes/get_quiz_data_by_uid&<uid>')
def get_quiz_data(uid):
    return handle_cm_func(Communicator.get_quiz_data, uid)
