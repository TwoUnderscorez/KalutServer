import SSLbottle as blt
import KalutServer.Model.Communicator as cm

@blt.get('/')
def test():
    return 'OK'

def start_server():
    srv = blt.SSLWSGIRefServer(host="192.168.1.160", port=25565)
    blt.run(server=srv)
