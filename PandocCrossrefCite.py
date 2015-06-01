# -*- coding: utf-8 -*-
import sublime
import sublime_plugin
import re
import os


def find_md_files(view):
    filename = view.file_name()
    name = os.path.basename(filename)
    dirname = os.path.dirname(filename)
    filelist = os.listdir(dirname)
    mdf_reg = re.compile("^.*?(\.md|\.markdown|\.mdown|\.pandoc)")
    md_files = []
    for f in filelist:
        match = mdf_reg.match(f)
        if match:
            md_files.append(match.group())
    md_files.remove(name)

    return(md_files, dirname, name)


def get_labels(view):
    # trouver l'ensemble des références à un tableau ou une figure dans view
    # regex pour les labels
    tbl_reg = re.compile("^\w*:(.*?){#(tbl):([a-zA-Z0-9-_]*)?}")
    fig_reg = re.compile("^.*\!\[(.*?)\]\(.*?\)\s*{#(fig):([a-zA-Z0-9-_]*)?}")
    eq_reg = re.compile("^\${2}(.*)\${2}\s*{#(eq):(.*?)}")
    code_reg = re.compile("^(?:`{3}|~{3}){#(lst):(\w*).*caption=\"(.*)\"}")
    # récupérer l'ensemble du texte
    content = view.split_by_newlines(sublime.Region(0, view.size()))
    labels = []
    for elmt in content:
        line = view.substr(elmt)
        match = tbl_reg.match(line)
        if not match:
            match = fig_reg.match(line)
            if not match:
                match = code_reg.match(line)
                if not match:
                    match = eq_reg.match(line)
        if match:
            caption = match.group(1)
            genre = match.group(2)
            label = match.group(3)
            labels.append({
                "caption": caption.strip(),
                "genre": genre,
                "label": label
                })
    return(labels)


# redefine function get_label so it doesn't need
# to know wether input is current buffer or
# external file.
# then write two functions, one for current buffer
# content = view.split...
# one for external file.
# then check in PandocCrossrefCiteCommand if
# 1. option check for external file is on (pref.)
# 2. there are other markdown files in folder
# if not, function stays the same
# if yes, then parse those files, extract reference
# and add it to completions, with an indication it's
# in another file

class PandocCrossrefCiteCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        view = self.view
        point = view.sel()[0].b
        completions = get_labels(view)

        g = sublime.load_settings("PandocTools.sublime-settings")
        restrict_to_markdown = g.get("PandocCite_restrict", "True")

        # Attention, ceci dépend de la coloration syntaxique utilisée
        doc_is_markdown = view.score_selector(point, "text.markdown")

        if not doc_is_markdown and restrict_to_markdown:
            return

        def on_done(i):
            if i < 0:
                return

            cite = "[@" + completions[i]["genre"] + ":" + completions[i]["label"] + "]"
            view.run_command(
                "insert_cite",
                {"a": point, "b": point, "cite": cite})


        completion_strings = [entry['genre'] + " : " + entry['caption'] + " (" + entry['label'] + ")" for entry in completions]
        view.window().show_quick_panel(completion_strings, on_done)
