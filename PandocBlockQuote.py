# -*- coding: utf-8 -*-
import sublime
import sublime_plugin
import re


class PandocBlockQuoteCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        view = self.view
        point = view.sel()[0].b
        last_point_previous_line = view.line(point).a-1

        line = view.substr(sublime.Region(view.line(point).a, point))
        previous_line = view.substr(sublime.Region(
            view.line(last_point_previous_line).a, last_point_previous_line))

        empty_blockquote_trigger = re.compile("^> $")

        empty_line = empty_blockquote_trigger.match(line)
        empty_previous_line = empty_blockquote_trigger.match(previous_line)

        if empty_line and empty_previous_line:
            self.view.replace(edit,
                              sublime.Region(view.line(last_point_previous_line).a,point),
                              "\n")
        else:
            self.view.insert(edit, point, "\n"+"> ")
