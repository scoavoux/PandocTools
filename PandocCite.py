# -*- coding: utf-8 -*-
import sublime
import sublime_plugin
import re
from collections import defaultdict
from . import warning
import PandocTools.bibparser as bibparser

# On sépare la récupération des données bibtex
def get_bib_data(view):
    s = sublime.load_settings("PandocTools.sublime-settings")
    bib_files = s.get("bibfiles")
    print ("Bib files found: ")
    print (repr(bib_files))

    if not bib_files:
        raise NoBibFilesError()

    bib_files = ([x.strip() for x in bib_files])

    print ("Files:")
    print (repr(bib_files))

    bib_data = bibparser.parse_bibtex(bib_files,exceptions=["@comment","@string"])

    print ( "Found %d total bib entries" % (len(bib_data),) )

    return bib_data

# This function comes from LatexTools cite_completions.py.
# Instead of looking through the file to find linked bib files
# it just imports a list of bibfile from PandocTools.sublime
def get_cite_completions(view,bib_data):
    def shorten_author(authors):
        last_name = lambda author : author.split(", ")[0].strip(' ')
        if authors :
            authors = [last_name(one_author) for one_author in authors.split(" and ")]

            # get last name for 'first last' format (preserve {...} text)
            # What the hell is that ?
            authors = [a.split(" ")[-1] if a[-1] != '}' or a.find('{') == -1 else re.sub(r'{|}', '', a[len(a) - a[::-1].index('{'):-1]) for a in authors]

            if len(authors) > 2:
                authors = authors[0] + " et al."
            else:
                authors = ' & '.join(authors)
        return authors

    def shorten_title(title,sep):
        truncated = sep.split(title)[0]
        return truncated[0:60] + '...' if len(truncated) > 60 else truncated 

    sep = re.compile("[:.?]")
    completions = []

    for keyword in bib_data :
        entry = defaultdict(lambda : None,bib_data[keyword])
        title = entry["title"] or entry["chapter"] or ""
        author = entry["author"] or entry["editor"] or ""
        completions.append({
                    "keyword" : keyword,
                    "title" : title,
                    "title_short": shorten_title(title,sep),
                    "author_short": shorten_author(author),
                    "year" : entry["year"],
                    "author" : author,
                    "journal" : entry["journal"] or entry["booktitle"] or ""
                    })

    return  completions

def prefilter_completions(point,line,unfiltered):
    # La clé est un début d'entrée de l'utilisateur,
    # utilisée pour pré-filtrer les match

    # On cherche si le curseur est précédé d'une éventuelle arobase et d'un point-virgule ou un crochet
    # [@toto,@tata -> on veut capturer "@tata"
    # [toto -> on veut capturer "toto"
    # [@toto; tata -> on veut capturer "tata"
    # [@toto      -> on veut capturer "@toto"
    # Comme on veut matcher depuis la fin de la ligne, 
    # On renverse ligne et regex
    reversed_line = line[::-1]
    cite_trigger = re.compile("([^,^;]*?@?)([;,].+?\[|\[)")
                            # First group : (the key)
                            # Anything that isn't a comma or a semicolon (greedy)
                            # Followed by a facultative "@"
                            # Second group :
                            # A semicolon or comma followed  by something (greedy) and a [
                            # or just a [
    print(cite_trigger)

    # Match
    match = cite_trigger.match(reversed_line)
    if match :
        # On récupère le groupe qui constitue la clé
        # Le second groupe contient ";(...)[" ou '[', il est inutile
        key = match.groups()[0][::-1]
        print(match.groups()[0])

        # On calcule le point qui débutera la region a remplacer (arobase)
        point = point-len(key)

        # L'arobase ne nous sert plus à rien
        key = key.lstrip("@")

        # Filtrage, on ignore la case
        completions = [entry_dict for entry_dict in unfiltered if any(elem and (key.lower() in entry_dict[elem].lower()) for elem in entry_dict)]

        # Si on n'a pas trouvé d'entrées
        if not completions :
            warning.warning("Aucune entrée bibliographique ne correspond au mot clé :'{}'. Mot clé ignore.".format(key))
            completions = unfiltered
    else:
        completions = unfiltered 	

    # En l'absence de match, completions = unfiltered, et point n'a pas changé
    return completions,point

class PandocCiteCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        view = self.view
        point = view.sel()[0].b

        # Prefs
        g = sublime.load_settings("PandocTools.sublime-settings")
        cite_panel_format = g.get("cite_panel_format", ["{title} ({keyword})", "{author}"])
        restrict_to_markdown = g.get("PandocCite_restrict", "True") 

        ## Attention, ceci dépend de la coloration syntaxique utilisée
        doc_is_markdown = view.score_selector(point,"text.markdown")

        if not doc_is_markdown and restrict_to_markdown :
            return

        # Récupérer la ligne et la liste de complétions biblio, pré-filtrer au besoin
        line = view.substr(sublime.Region(view.line(point).a, point))
        unfiltered = get_cite_completions(view,get_bib_data(view))

        if doc_is_markdown :
            prefix = "@"
            completions,beginning = prefilter_completions(point,line,unfiltered)
        else:
            prefix = ""
            completions,beginning = unfiltered,point
            # no pre-filtering if we're not in markdown.

        def on_done(i):
            if i<0:
                return

            cite = prefix + completions[i]["keyword"]
            view.run_command("insert_cite",{"a": beginning, "b": point, "cite": cite})


        completion_strings = [[formatter.format(**bib_dict) for formatter in cite_panel_format] for bib_dict in completions]

        view.window().show_quick_panel(completion_strings, on_done)


## This is because "Edit objects may not be used after the TextCommand's run method has returned"

# ST3 cannot use an edit object after the TextCommand has returned; and on_done gets 
# called after TextCommand has returned. Thus, we need this work-around (works on ST2, too)
class InsertCiteCommand(sublime_plugin.TextCommand):
    def run(self,edit,a,b,cite):
        region = sublime.Region(a,b)            # Trouver la région entre a et b
        self.view.replace(edit,region,cite)     # remplacer ce texte par cite