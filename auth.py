import time
import random
import string
import urlparse
import urllib
import hashlib

import tornado.web
import tornado.template
import tornado.auth
import tornado.escape

from setting import settings


import functools
from tornado import httpclient
from tornado import escape

class QQMixin(tornado.auth.OAuth2Mixin):
    _OAUTH_ACCESS_TOKEN_URL = "https://graph.qq.com/oauth2.0/token"
    _OAUTH_AUTHORIZE_URL = "https://graph.qq.com/oauth2.0/authorize"

    @tornado.web.asynchronous
    def get_authenticated_user(self, redirect_uri, client_id, client_secret,
                               code, callback, extra_fields=None):
        http = httpclient.AsyncHTTPClient()

        fields = set()
        if extra_fields:
            fields.update(extra_fields)

        args = {
            "redirect_uri": redirect_uri,
            "code": code,
            "client_id": client_id,
            "client_secret": client_secret,
            "grant_type": "authorization_code"
        }

        http.fetch(self._OAUTH_ACCESS_TOKEN_URL,
            self.async_callback(self._on_access_token, redirect_uri, client_id, client_secret, callback, fields),
            method="POST", body=urllib.urlencode(args))

    @tornado.web.asynchronous
    def _on_access_token(self, redirect_uri, client_id, client_secret,
                         callback, fields, response):
        args = escape.parse_qs_bytes(escape.native_str(response.body))

        #self.finish({"body":response.body, "args":args})
        session = {
            "access_token": args["access_token"][-1],
            "refresh_token": args["refresh_token"][-1],
            "expires_in": args["expires_in"][-1]
        }

        callback(session)



class QQHandler(tornado.web.RequestHandler,
                QQMixin):
    @tornado.web.asynchronous
    def get(self):
        redirect_uri = "%s://%s%s" % (self.request.protocol, self.request.host, self.request.path)
        code = self.get_argument("code", None)
        if code:
            self.get_authenticated_user(redirect_uri, settings["QQAppID"], settings["QQAppKey"],
                                   code, self._on_auth)
            return
        self.authorize_redirect(redirect_uri,
                                client_id=settings["QQAppID"],
                                extra_params={"response_type": "code"})

    def _on_auth(self, session):
        self.finish(session)


class LogoutHandler(tornado.web.RequestHandler):
    def get(self):
        self.redirect_url = self.get_argument("next", "/")
        self.clear_cookie("user")
        self.redirect(self.redirect_url)
