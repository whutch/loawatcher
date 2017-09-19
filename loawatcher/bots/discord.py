# -*- coding: utf-8 -*-
"""Interface for Discord bots."""
# Part of Watcher (https://github.com/whutch/loawatcher)
# :copyright: (c) 2017 Will Hutcheson
# :license: MIT (https://github.com/whutch/loawatcher/blob/master/LICENSE.txt)

import asyncio

import discord
from discord.ext import commands

from .. import settings


DISCORD = settings.SECRETS["discord"]


class DiscordBot:

    """A Discord bot."""

    def __init__(self):
        self._bot = None
        self._channel = None
        self._loop = asyncio.get_event_loop()
        self._server = None

    def start(self):
        self._bot = commands.Bot(
            command_prefix=settings.COMMAND_PREFIX,
            description=settings.DESCRIPTION)
        self._bot.event(self.on_ready)
        self._bot.event(self.on_message)
        self._loop.create_task(self._bot.start(DISCORD["token"]))

    def send_message(self, msg):
        self._loop.create_task(self._bot.send_message(self._channel, msg))

    @asyncio.coroutine
    def on_ready(self):
        print("Logged in as {} {}".format(self._bot.user.name, self._bot.user.id))
        self._server = self._bot.get_server(DISCORD["server"])
        self._channel = self._bot.get_channel(DISCORD["channel"])

    @asyncio.coroutine
    def on_message(self, message):
        print("{}: {}".format(message.author.display_name, message.content))
        yield from self._bot.process_commands(message)
