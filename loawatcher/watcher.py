# -*- coding: utf-8 -*-
"""Primary server logic."""
# Part of Watcher (https://github.com/whutch/loawatcher)
# :copyright: (c) 2017 Will Hutcheson
# :license: MIT (https://github.com/whutch/loawatcher/blob/master/LICENSE.txt)

import asyncio
import re

from . import settings
from .bots.discord import DiscordBot
from .cli import CLI
from .logs import get_logger


LOG = get_logger()
LOOP = asyncio.get_event_loop()
BOT = DiscordBot()


class DoNotOutput(Exception):
    """An exception for cancelling output inside the formatter."""


class UDPProtocol(asyncio.DatagramProtocol):

    def __init__(self, message_handler):
        self.message_handler = message_handler

    def datagram_received(self, data, addr):
        msg = data.decode()
        LOOP.create_task(self.message_handler(msg))

    @classmethod
    def create(cls):
        return cls(handle_message)


class GameObj:

    def __init__(self, name, obj_id, user_id=None):
        self.name = name
        self.obj_id = obj_id
        self.user_id = user_id

    def __format__(self, format_type):
        if format_type == "long":
            user_id = ":{}".format(self.user_id) if self.user_id else ""
            return "{}:{}{}".format(self.obj_id, self.name, user_id)
        user_id = " ({})".format(self.user_id) if self.user_id else ""
        return "{}{}".format(self.name, user_id)


class Loc:

    def __init__(self, world, x, y, z, region=None):
        self.world = world
        self.x = x
        self.y = y
        self.z = z
        self.region = region

    def __format__(self, format_type):
        if format_type == "long":
            return "{}:({},{},{})".format(self.world, self.x, self.y, self.z)
        return "({},{},{})".format(self.x, self.y, self.z)


class ChatMessage:

    def __init__(self, message):
        self.message = message

    def __format__(self, format_type):
        if format_type == "filtered":
            match = re.search("bank", self.message)
            if match:
                raise DoNotOutput
        return self.message


def lua_int(string):
    if '.' in string:
        return float(string)
    else:
        return int(string)


TYPE_CODES = {
    "i": lua_int,
    "s": str,
    "b": bool,
    "G": GameObj,
    "L": Loc,
}


OUTPUT_HANDLERS = {
    "log": LOG.info,
    "discord": BOT.send_message,
}


MSG_FORMATS = {
    "CHAT": {
        "SAY": {
            "discord": "{} said '{:filtered}' @{}.",
            "log": "{:long} said '{}' @{:long}.",
        },
    },
    "COMBAT": {
        "DEATH": {
            "discord": "{} was killed by {} @{}.",
            "log": "{:long} was killed by {:long} @{:long} (damagers table: {}).",
        },
    },
    "CRIME": {
        "ATTACK": {
            "discord": "{} attacked {} @{}.",
            "log": "{:long} attacked {:long} @{:long}.",
        },
        "MURDER": {
            "discord": "{} murdered {} @{}.",
            "log": "{:long} murdered {:long} @{:long}.",
        },
        "STEAL": {
            "discord": "{} stole {} from {} @{}.",
            "log": "{} stole {} from {} @{}.",
        },
    },
    "PLAYER": {
        "CREATE": {
            "discord": "{} was created!",
            "log": "{:long} was created!",
        },
        "DELETE": {
            "discord": "{} was deleted @{}!",
            "log": "{:long} was deleted @{:long}!",
        },
        "LOGIN": {
            "discord": "{} has logged in @{}.",
            "log": "{:long} has logged in @{:long}.",
        },
        "LOGOUT": {
            "discord": "{} has logged out @{}.",
            "log": "{:long} has logged out @{:long}.",
        },
    },
    "SERVER": {
        "BOOT": {
            "discord": "Server has booted.",
            "log": "Server has booted.",
        },
        "REGION_START": {
            "discord": "Region '{}' has started.",
            "log": "Region '{}' has started.",
        },
        "RESTART": {
            "discord": "Server reboot by {}, reason is '{}'.",
            "log": "Server reboot by {:long}, reason is '{}'.",
        },
        "SHUTDOWN": {
            "discord": "Server shutdown by {}, reason is '{}'.",
            "log": "Server shutdown by {:long}, reason is '{}'.",
        },
    },
}


def handle_message(message):
    msg_parts = message.split(settings.MSG_SEP)
    if len(msg_parts) != 3:
        return LOG.warning("Received malformed message '%s'.", message)
    msg_type, msg_subtype, obj_strings = msg_parts
    subtypes = MSG_FORMATS.get(msg_type)
    if not subtypes:
        return LOG.warning("Unknown message type '%s'.", msg_type)
    output_formats = subtypes.get(msg_subtype)
    if not output_formats:
        return LOG.warning("Unknown message subtype '%s'.", msg_subtype)
    converted_objs = []
    for obj_string in obj_strings.split(settings.OBJ_SEP):
        if not obj_string:
            continue
        type_code, *obj_data = obj_string.split(settings.DATA_SEP)
        obj_type = TYPE_CODES.get(type_code)
        if not obj_type:
            return LOG.warning("Unknown object type code '%s' with data '%s'.", type_code, obj_data)
        converted_objs.append(obj_type(*obj_data))
    # Temporary until something less hard-coded can be thought up.
    if msg_type == "CHAT":
        converted_objs[1] = ChatMessage(converted_objs[1])
    # All data has been processed.
    LOG.debug("Received message %s:%s '%s'.", msg_type, msg_subtype, obj_strings)
    for output_type, format_string in output_formats.items():
        handler = OUTPUT_HANDLERS.get(output_type)
        if handler:
            try:
                output = format_string.format(*converted_objs)
            except DoNotOutput:
                pass
            else:
                handler(output)


def handle_exception(loop, context):
    print(context)


def run():
    # Bind the UDP listener and set up a message handler.
    LOOP.run_until_complete(LOOP.create_datagram_endpoint(
        UDPProtocol.create, local_addr=(CLI.args.host, CLI.args.port)))
    # Initiate the Discord bot.
    BOT.start()
    # Start the event loop.
    try:
        LOOP.set_exception_handler(handle_exception)
        LOOP.run_forever()
    except KeyboardInterrupt:
        pass
