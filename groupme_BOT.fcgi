#!/usr/bin/python
from flup.server.fcgi import WSGIServer
from groupme-BOT import app

if __name__ == '__main__':
    WSGIServer(app).run()