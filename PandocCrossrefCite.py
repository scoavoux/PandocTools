# -*- coding: utf-8 -*-
import sublime
import sublime_plugin
import re


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
