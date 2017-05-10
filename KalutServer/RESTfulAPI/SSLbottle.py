from bottle import Bottle, run, ServerAdapter, get, post
class SSLWSGIRefServer(ServerAdapter):
    def run(self, handler):
        from wsgiref.simple_server import make_server, WSGIRequestHandler
        import ssl
        if self.quiet:
            class QuietHandler(WSGIRequestHandler):
                def log_request(*args, **kw): pass
            self.options['handler_class'] = QuietHandler
        srv = make_server(self.host, self.port, handler, **self.options)
        srv.socket = ssl.wrap_socket (
            srv.socket,
            certfile='C:\\rsa_keys\\planq.tk-chain.pem',  # path to chain file
            keyfile='C:\\rsa_keys\\planq.tk-key.pem',     # path to RSA private key
            server_side=True)
        srv.serve_forever()
