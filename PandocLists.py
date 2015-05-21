# -*- coding: utf-8 -*-
import sublime
import sublime_plugin
import re


class PandocListsCommand(sublime_plugin.TextCommand):
  def run(self, edit):
    view = self.view
    point = view.sel()[0].b
    line = view.substr(sublime.Region(view.line(point).a, point))
    bullets_trigger = re.compile("^([*-+]|#\.) .+")
    numeric_list_trigger = re.compile("^(\d+)([.)]) .+")

    bullet = bullets_trigger.match(line)
    numeric = numeric_list_trigger.match(line)

    if bullet:
        new_bullet = bullet.groups()[0]
    elif numeric:
        new_bullet = str(int(numeric.groups()[0])+1)+numeric.groups()[1]

    self.view.insert(edit, point, "\n"+new_bullet+" ")