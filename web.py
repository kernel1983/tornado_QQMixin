import sys
import os

import logging
import uuid
import urlparse
import urllib
import time

import tornado.options
import tornado.ioloop
import tornado.web


from setting import settings

import auth

application = tornado.web.Application([
    (r"/logout", auth.LogoutHandler),
    (r"/", auth.QQHandler),
], **settings)

if __name__ == "__main__":
    tornado.options.define("port", default=8000, help="Run server on a specific port", type=int)
    tornado.options.parse_command_line()
    application.listen(tornado.options.options.port)
    tornado.ioloop.IOLoop.instance().start()

