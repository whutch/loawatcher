# -*- coding: utf-8 -*-
"""Requesting data from the LoA server."""
# Part of Watcher (https://github.com/whutch/loawatcher)
# :copyright: (c) 2017 Will Hutcheson
# :license: MIT (https://github.com/whutch/loawatcher/blob/master/LICENSE.txt)

import asyncio
import socket
import uuid

from . import settings


REQUESTS = set()
RESPONSES = {}


@asyncio.coroutine
def request_data(request_type):
    request_id = str(uuid.uuid4())
    if request_id in REQUESTS:
        raise KeyError("Error creating multiple requests in the same frame.")
    request = settings.MSG_SEP.join(["REQUEST", request_id, request_type]) + "\n"
    loa_server = (settings.SERVER_HOST, settings.SERVER_PORT)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(loa_server)
    sock.send(request.encode())
    sock.close()

    REQUESTS.add(request_id)
    while request_id not in RESPONSES:
        yield from asyncio.sleep(0.25)
    REQUESTS.remove(request_id)
    data = RESPONSES.pop(request_id)
    return data
