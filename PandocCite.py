# -*- coding: utf-8 -*-
import sublime, sublime_plugin
import re
import codecs
from collections import defaultdict

## Additions Sarah !
import bibparser

# This function comes from LatexTools cite_completions.py.
# Instead of looking through the file to find linked bib files
# it just imports a list of bibfile from PandocTools.sublime
def get_cite_completions(view):

	#
	s = sublime.load_settings("PandocTools.sublime-settings")
	bib_files = s.get("bibfiles")
	# remove duplicate bib files
	print ("Bib files found: ")
	print (repr(bib_files))

	if not bib_files:
		# sublime.error_message("No bib files found!") # here we can!
		raise NoBibFilesError()

	bib_files = ([x.strip() for x in bib_files])

	print ("Files:")
	print (repr(bib_files))

	bib_data = bibparser.parse_bibtex(bib_files,exceptions=["@comment","@string"])

	print ( "Found %d total bib entries" % (len(bib_data),) )

	keywords = []
	titles = []
	authors = []
	years = []
	journals = []

	for keyword in bib_data :
		entry = defaultdict(lambda : None,bib_data[keyword])
		keywords.append(keyword)
		titles.append(entry["title"] or entry["chapter"] or "")
		years.append(entry["year"])
		# For author, if there is an editor, that's good enough
		authors.append(entry["author"] or entry["editor"] or "")
		journals.append(entry["journal"] or entry["booktitle"] or "")
		
	# format author field
	def format_author(authors):
		if authors :
			# print(authors)
			# split authors using ' and ' and get last name for 'last, first' format
			authors = [a.split(", ")[0].strip(' ') for a in authors.split(" and ")]
			# get last name for 'first last' format (preserve {...} text)
			authors = [a.split(" ")[-1] if a[-1] != '}' or a.find('{') == -1 else re.sub(r'{|}', '', a[len(a) - a[::-1].index('{'):-1]) for a in authors]
			#     authors = [a.split(" ")[-1] for a in authors]
			# truncate and add 'et al.'
			if len(authors) > 2:
				authors = authors[0] + " et al."
			else:
				authors = ' & '.join(authors)
			# return formated string
			# print(authors)
		return authors

	# format list of authors
	authors_short = [format_author(author) for author in authors]

	# short title
	sep = re.compile("[:.?]")
	titles_short = [sep.split(title)[0] for title in titles]
	titles_short = [title[0:60] + '...' if len(title) > 60 else title for title in titles_short]


	#### END COMPLETIONS HERE ####

	return  zip(keywords, titles, authors, years, authors_short, titles_short, journals)

def prefilter_completions(point,line,completions):
	# La clé est un début d'entrée de l'utilisateur,
	# utilisée pour pré-filtrer les match

	# On cherche si le curseur est précédé de : [@.*
	# Comme on veut matcher depuis la fin de la ligne, 
	# On renverse ligne et regex
	reversed_line = line[::-1]
	cite_trigger = re.compile("\]?(.+?@?)\[")

	# Match
	match = cite_trigger.match(reversed_line)
	if match :
		# On récupère le groupe qui constitue la clé
		key = match.groups()[0][::-1]

		# On calcule le point qui débutera la région à remplacer
		beginning = point-len(key)

		key = key.lstrip("@")

		# Filtrage, on ignore la case
		completions = [comp for comp in completions if any(elem and (key.lower() in elem.lower()) for elem in comp)]

		if not completions :
			# Message d'erreur
			# Mot clé = key : n'insèrera ni ne supprimera rien
			completions = [(key,"Aucune entree bibliographique ne correspond","Erreur","","","Pas de correspondance","")]
	else:
		# Pas de clé, remplacement simple
		beginning = point
		key = ""


	return completions,beginning

class PandocCiteCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		view = self.view
		point = view.sel()[0].b
		g = sublime.load_settings("PandocTools.sublime-settings")
		cite_panel_format = g.get("cite_panel_format", ["{title} ({keyword})", "{author}"])
	
		if not view.score_selector(point,"text.markdown"):
			return

		line = view.substr(sublime.Region(view.line(point).a, point))
		completions_all = get_cite_completions(view)

		completions,beginning = prefilter_completions(point,line,completions_all)

		def on_done(i):

			if i<0:
				return

			cite = "@" + completions[i][0]
			view.run_command("insert_cite",{"a":beginning,"b":point,"ins":cite})			
		

		view.window().show_quick_panel([[str.format(keyword=keyword, title=title, author=author, year=year, author_short=author_short, title_short=title_short, journal=journal) for str in cite_panel_format] \
				for (keyword, title, author, year, author_short, title_short,journal) in completions], on_done)
		#view.window().show_quick_panel("123",on_done)

class InsertCiteCommand(sublime_plugin.TextCommand):
	def run(self,edit,a,b,ins):
			region = sublime.Region(a,b)
			self.view.replace(edit,region,ins)

