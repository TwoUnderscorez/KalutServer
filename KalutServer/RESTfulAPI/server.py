import SSLbottle as blt
from KalutServer.Exceptions import *
from KalutServer.Model.Communicator import Communicator
import KalutServer.conf as myconf
import json

def build_standart_response(data, status='OK', errMsg=None):
    return {
        'Status' : status,
        'Data' : data,
        'ErrMsg' : errMsg
    }
 
def handle_cm_func(func, *args):
    model = Communicator()
    data = func(model, *args)
    model.logout()
    return build_standart_response(data)

def start_server():
    srv = blt.SSLWSGIRefServer(host=myconf.host, port=myconf.restapi_port)
    blt.run(server=srv)

## /    (general)
@blt.post('/auth')
def auth():
    usrname = blt.request.json.get('Username')
    pwd = blt.request.json.get('Password')
    return handle_cm_func(Communicator.auth_user, usrname, pwd)

@blt.get('/')
def test():
    return build_standart_response({
            'Service Status' : 'OK' 
        })

@blt.get('/rooms/create_room&<uid>')
def create_room(uid):
    return handle_cm_func(Communicator.create_room, uid)

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

@blt.post('/quizes/get_user_kaluts_info')
def get_user_kaluts_info():
    usrname = blt.request.json.get('Username')
    pwd = blt.request.json.get('Password')
    return handle_cm_func(Communicator.get_user_kaluts, usrname, pwd)

@blt.post('/quizes/get_user_fav_kaluts_info')
def get_user_kaluts_fav_info():
    usrname = blt.request.json.get('Username')
    pwd = blt.request.json.get('Password')
    return handle_cm_func(Communicator.get_user_fav_kaluts, usrname, pwd)

@blt.post('/quizes/add')
def add_quiz():
    usrname = blt.request.json.get('Username')
    pwd = blt.request.json.get('Password')
    quiz_data = blt.request.json.get('QuizData')
    quiz_desc = blt.request.json.get('QuizDescription')
    return handle_cm_func(Communicator.add_kalut, usrname, pwd, quiz_desc, quiz_data)