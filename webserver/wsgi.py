from gevent.wsgi import WSGIServer
from app import app

http_server = WSGIServer(('', 44442), app)
http_server.serve_forever()
