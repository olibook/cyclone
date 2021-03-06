# coding: utf-8
#
# Copyright 2010 Alexandre Fiori
# based on the original Tornado by Facebook
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from cyclone.web import RequestHandler
from twisted.python import log

class SSEHandler(RequestHandler):
    def __init__(self, application, request):
        RequestHandler.__init__(self, application, request)
        self.transport = request.connection.transport
        self._auto_finish = False

    def sendEvent(self, message, event=None, eid=None, retry = None):
        """
        sendEvent is the single method to send events to clients.
        message: the event itself
        event: optional event name
        eid: optional event id to be used as Last-Event-ID header or e.lastEventId property
        retry: set the retry timeout in ms. default 3 secs.
        """
        if isinstance(message, dict):
            message = escape.json_encode(message)
        if isinstance(message, unicode):
            message = message.encode("utf-8")
        assert isinstance(message, str)

        if eid:
            self.transport.write("id: %s\n" % eid)
        if event:
            self.transport.write("event: %s\n" % event)
        if retry:
            self.transport.write("retry: %s\n" % retry)

        self.transport.write("data: %s\n\n" % message)

    def _execute(self, transforms, *args, **kwargs):
        self._transforms = [] # transforms
        if self.settings.get("debug"):
            log.msg("SSE connection from %s" % self.request.remote_ip)
        self.set_header("Content-Type", "text/event-stream")
        self.set_header("Cache-Control", "no-cache")
        self.set_header("Connection", "keep-alive")
        self.flush()
        self.request.connection.setRawMode()
        self.notifyFinish().addCallback(self.on_connection_closed)
        self.bind()

    def on_connection_closed(self, *args, **kwargs):
        if self.settings.get("debug"):
            log.msg("SSE client disconnected %s" % self.request.remote_ip)
        self.unbind()

    def bind(self):
        pass

    def unbind(self):
        pass
