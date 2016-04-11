# -*- coding: utf-8 -*-
import sublime
import sublime_plugin
import re


class PandocListsCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        view = self.view
        point = view.sel()[0].b
        line = view.substr(sublime.Region(view.line(point).a, point))
        bullets_trigger = re.compile("^( *)([*-+]|#\.) .+")
        numeric_list_trigger = re.compile("^( *)([(])?(\d+)([.)]) .+")

        bullet = bullets_trigger.match(line)
        numeric = numeric_list_trigger.match(line)
        spaces = ""

        if bullet:
            spaces = bullet.groups()[0]
            new_bullet = bullet.groups()[1]
        elif numeric:
            spaces = numeric.groups()[0]
            before = numeric.groups()[1] or ""
            new_bullet = before+str(int(numeric.groups()[2])+1)+numeric.groups()[3]

        self.view.insert(edit, point, "\n"+spaces+new_bullet+" ")
