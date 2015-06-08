# -*- coding: utf-8 -*-
import sublime
import sublime_plugin
import re


class PandocIndentOne(sublime_plugin.TextCommand):
  def run(self, edit):
    view = self.view
    point = view.sel()[0].b
    start = view.line(point).a
    self.view.insert(edit, start, "\t")