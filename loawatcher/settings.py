# -*- coding: utf-8 -*-
"""Core settings and configuration."""
# Part of Watcher (https://github.com/whutch/loawatcher)
# :copyright: (c) 2017 Will Hutcheson
# :license: MIT (https://github.com/whutch/loawatcher/blob/master/LICENSE.txt)

import json
from os import getcwd
from os.path import join


DEBUG = False
TESTING = False

# Networking
DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 10000

# LoA Server
SERVER_HOST = "127.0.0.1"
SERVER_PORT = 10001
MSG_SEP = "\x1c"
OBJ_SEP = "\x1d"
DATA_SEP = "\x1e"

# Logging
LOG_PATH = join(getcwd(), "logs", "watcher.log")
LOG_TIME_FORMAT_CONSOLE = "%H:%M:%S,%F"
LOG_TIME_FORMAT_FILE = "%Y-%m-%d %a %H:%M:%S,%F"
LOG_ROTATE_WHEN = "midnight"
LOG_ROTATE_INTERVAL = 1
LOG_UTC_TIMES = False

# Storage
DATA_DIR = join(getcwd(), "data")

# Bots
DESCRIPTION = "Watcher bot."
COMMAND_PREFIX = "?"


with open("secrets.json") as secrets_file:
    SECRETS = json.load(secrets_file)
