import SSLbottle as blt
from KalutServer.Model.Communicator import Communicator 
import json

def build_standart_response(data, status='OK', errMsg=None):
    return {
        'Status' : status,
        'Data' : data,
        'ErrMsg' : errMsg
    }

@blt.get('/')
def test():
    return build_standart_response({
            'Service Status' : 'OK' 
        })
 
def handle_cm_func(func, *args):
    model = Communicator()
    data = func(model, *args)
    model.logout()
    return build_standart_response(data)

def start_server():
    srv = blt.SSLWSGIRefServer(host="192.168.1.160", port=25565)
    blt.run(server=srv)

## /    (general)
@blt.post('/auth')
def auth():
    usrname = blt.request.json.get('Username')
    pwd = blt.request.json.get('Password')
    return handle_cm_func(Communicator.auth_user, usrname, pwd)
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