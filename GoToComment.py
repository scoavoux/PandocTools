# -*- coding: utf-8 -*-
# import sublime
import sublime_plugin


class GotoNextCommentCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        comments_reg = self.view.find_all("<!--")
        point = self.view.sel()[0].b
        for reg in comments_reg:
            if point+1 > reg.a:
                next
            else:
                self.view.sel().clear()
                self.view.sel().add(reg.a)
                self.view.show(reg)
                return


class GotoPreviousCommentCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        comments_reg = self.view.find_all("<!--")
        point = self.view.sel()[0].b
        for reg in comments_reg[::-1]:
            if point-1 < reg.a:
                next
            else:
                self.view.sel().clear()
                self.view.sel().add(reg.a)
                self.view.show(reg)
                return
