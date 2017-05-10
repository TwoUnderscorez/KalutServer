import SSLbottle as blt
import KalutServer.Model.Communicator as cm


def run():
    srv = blt.SSLWSGIRefServer(host="0.0.0.0", port=8090)
    blt.run(server=srv)
