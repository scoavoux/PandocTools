# -*- coding: utf-8 -*-
import sublime


def warning(msg):
    msg = "Warning: " + msg
    print(msg)
    sublime.status_message(msg)
