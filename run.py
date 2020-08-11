from HomeTerminal import create_app

if __name__ == "__main__":
    from gevent import pywsgi
    from geventwebsocket.handler import WebSocketHandler
    app = create_app()
    server = pywsgi.WSGIServer(('localhost', 5050), app, handler_class=WebSocketHandler, log=app.logger)
    server.serve_forever()
