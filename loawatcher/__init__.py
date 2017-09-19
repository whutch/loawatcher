# -*- coding: utf-8 -*-
"""Companion server for Legends of Aria."""
# Part of Watcher (https://github.com/whutch/loawatcher)
# :copyright: (c) 2017 Will Hutcheson
# :license: MIT (https://github.com/whutch/loawatcher/blob/master/LICENSE.txt)

from os.path import abspath, dirname


VERSION = (0, 1, 0, 0)
ROOT_DIR = dirname(dirname(abspath(__file__)))
BASE_PACKAGE = __name__


def get_version():
    """Return the version string."""
    return "{}{}".format(".".join([str(n) for n in VERSION[:3]]),
                         "" if VERSION[3] == 0
                         else ".dev{}".format(VERSION[3]))


__author__ = "Will Hutcheson"
__contact__ = "will@whutch.com"
__homepage__ = "https://github.com/whutch/loawatcher"
__license__ = "MIT"
__docformat__ = "restructuredtext"
__version__ = get_version()
