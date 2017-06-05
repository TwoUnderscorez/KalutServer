from mybottle import Bottle, run, ServerAdapter, get, post, request
import KalutServer.conf as myconf
class SSLWSGIRefServer(ServerAdapter):
    def run(self, handler, quiet=False):
        from wsgiref.simple_server import make_server, WSGIRequestHandler
        import ssl
        if quiet:
            class QuietHandler(WSGIRequestHandler):
                def log_request(*args, **kw): pass
            self.options['handler_class'] = QuietHandler
        srv = make_server(self.host, self.port, handler, **self.options)
        srv.socket = ssl.wrap_socket (
            srv.socket,
            certfile=myconf.certfile,  # path to chain file
            keyfile=myconf.keyfile,    # path to RSA private key
            server_side=True)
        srv.serve_forever()
