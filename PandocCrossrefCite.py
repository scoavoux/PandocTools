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


def get_labels(view,fn):
    # trouver l'ensemble des références à un tableau ou une figure dans view
    # regex pour les labels
    tbl_reg = re.compile("^\w*:(.*?){#(tbl):([a-zA-Z0-9-_]*)?}")
    fig_reg = re.compile("^.*\!\[(.*?)\]\(.*?\)\s*{.*?#(fig):([a-zA-Z0-9-_]*)?.*?}")
    eq_reg = re.compile("^\${2}(.*)\${2}\s*{#(eq):(.*?)}")
    code_reg = re.compile("^(?:`{3}|~{3}){#(lst):(\w*).*caption=\"(.*)\"}")
    sec_reg = re.compile("^(#+.*?){#(sec):(.*?)}")
    # récupérer l'ensemble du texte
    if isinstance(view, sublime.View):
        content = view.split_by_newlines(sublime.Region(0, view.size()))
        print(type(content[0]))
    elif isinstance(view, str):
        with open(view) as f:
            content = f.readlines()
    labels = []
    for elmt in content:
        if isinstance(view, sublime.View):
            line = view.substr(elmt)
        else:
            line = elmt
        match = tbl_reg.match(line)
        if not match:
            match = fig_reg.match(line)
            if not match:
                match = code_reg.match(line)
                if not match:
                    match = eq_reg.match(line)
                    if not match:
                        match = sec_reg.match(line)
        if match:
            caption = match.group(1)
            genre = match.group(2)
            label = match.group(3)
            labels.append({
                "caption": caption.strip(),
                "genre": genre,
                "label": label,
                "file": fn
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

        g = sublime.load_settings("PandocTools.sublime-settings")
        restrict_to_markdown = g.get("pandoc_cite_restrict")

        # Attention, ceci dépend de la coloration syntaxique utilisée
        doc_is_markdown = view.score_selector(point, "text.markdown")

        if not doc_is_markdown and restrict_to_markdown:
            return

        md_files, dirname, name = find_md_files(view)

        completions = get_labels(view,name + " (current file)")
        if g.get("pandoc_crossref_multifile"):
            for f in md_files:
                p = os.path.join(dirname, f)
                completions += get_labels(p,f)


        def on_done(i):
            if i < 0:
                return

            cite = "[@" + completions[i]["genre"] + ":" + completions[i]["label"] + "]"
            view.run_command(
                "insert_cite",
                {"a": point, "b": point, "cite": cite})
            self.view.sel().clear()
            self.view.sel().add(point + len(cite))



        completion_strings = [entry['file'] + "_" + entry['genre'] + " : " + entry['caption'] + " (" + entry['label'] + ")" for entry in completions]
        view.window().show_quick_panel(completion_strings, on_done)
