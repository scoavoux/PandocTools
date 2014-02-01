import sublime, sublime_plugin
import re
import codecs

## TODO
### Afficher en propre plutôt qu'en latex (par regex ou package python)
### Ajouter des exceptions et les possibilités d'erreurs

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

	completions = []
	kp = re.compile(r'@[^\{]+\{(.+),')
	# new and improved regex
	# we must have "title" then "=", possibly with spaces
	# then either {, maybe repeated twice, or "
	# then spaces and finally the title
	# # We capture till the end of the line as maybe entry is broken over several lines
	# # and in the end we MAY but need not have }'s and "s
	# tp = re.compile(r'\btitle\s*=\s*(?:\{+|")\s*(.+)', re.IGNORECASE)  # note no comma!
	# # Tentatively do the same for author
	# # Note: match ending } or " (surely safe for author names!)
	# ap = re.compile(r'\bauthor\s*=\s*(?:\{|")\s*(.+)(?:\}|"),?', re.IGNORECASE)
	# # Editors
	# ep = re.compile(r'\beditor\s*=\s*(?:\{|")\s*(.+)(?:\}|"),?', re.IGNORECASE)
	# # kp2 = re.compile(r'([^\t]+)\t*')
	# # and year...
	# # Note: year can be provided without quotes or braces (yes, I know...)
	# yp = re.compile(r'\byear\s*=\s*(?:\{+|"|\b)\s*(\d+)[\}"]?,?', re.IGNORECASE)

	# This may speed things up
	# So far this captures: the tag, and the THREE possible groups
	multip = re.compile(r'\b(author|title|year|editor|journal|eprint)\s*=\s*(?:\{|"|\b)(.+?)(?:\}+|"|\b)\s*,?\s*\Z',re.IGNORECASE)

	for bibfname in bib_files:
		# # THIS IS NO LONGER NEEDED as find_bib_files() takes care of it
		# if bibfname[-4:] != ".bib":
		#     bibfname = bibfname + ".bib"
		# texfiledir = os.path.dirname(view.file_name())
		# # fix from Tobias Schmidt to allow for absolute paths
		# bibfname = os.path.normpath(os.path.join(texfiledir, bibfname))
		# print repr(bibfname)
		try:
			bibf = codecs.open(bibfname,'r','UTF-8', 'ignore')  # 'ignore' to be safe
		except IOError:
			print ("Cannot open bibliography file %s !" % (bibfname,))
			sublime.status_message("Cannot open bibliography file %s !" % (bibfname,))
			continue
		else:
			bib = bibf.readlines()
			bibf.close()
		print ("%s has %s lines" % (repr(bibfname), len(bib)))

		keywords = []
		titles = []
		authors = []
		years = []
		journals = []
		#
		entry = {   "keyword": "", 
					"title": "",
					"author": "", 
					"year": "", 
					"editor": "",
					"journal": "",
					"booktitle": "",
					"eprint": "" }
		for line in bib:
			line = line.strip()
			# Let's get rid of irrelevant lines first
			if line == "" or line[0] == '%':
				continue
			if line.lower()[0:8] == "@comment":
				continue
			if line.lower()[0:7] == "@string":
				continue
			if line[0] == "@":
				# First, see if we can add a record; the keyword must be non-empty, other fields not
				if entry["keyword"]:
					keywords.append(entry["keyword"])
					titles.append(entry["title"])
					years.append(entry["year"])
					# For author, if there is an editor, that's good enough
					authors.append(entry["author"] or entry["editor"] or "????")
					journals.append(entry["journal"] or entry["booktitle"] or "")
					# Now reset for the next iteration
					entry["keyword"] = ""
					entry["title"] = ""
					entry["year"] = ""
					entry["author"] = ""
					entry["editor"] = ""
					entry["journal"] = ""
					entry["booktitle"] = ""
					entry["eprint"] = ""
				# Now see if we get a new keyword
				kp_match = kp.search(line)
				if kp_match:
					entry["keyword"] = kp_match.group(1) # No longer decode. Was: .decode('ascii','ignore')
				else:
					print ("Cannot process this @ line: " + line)
					print ("Previous record " + entry)
				continue
			# Now test for title, author, etc.
			# Note: we capture only the first line, but that's OK for our purposes
			multip_match = multip.search(line)
			if multip_match:
				key = multip_match.group(1).lower()     # no longer decode. Was:    .decode('ascii','ignore')
				value = multip_match.group(2)           #                           .decode('ascii','ignore')
				entry[key] = value
			continue

		# at the end, we are left with one bib entry
		keywords.append(entry["keyword"])
		titles.append(entry["title"])
		years.append(entry["year"])
		authors.append(entry["author"] or entry["editor"] or "????")
		journals.append(entry["journal"] or entry["eprint"] or "????")

		print ( "Found %d total bib entries" % (len(keywords),) )

		# # Filter out }'s at the end. There should be no commas left

		keywords = [k.lstrip() for k in keywords]

		## compléter les replace, ici et plus loin, pour corriger les problèmes de caractéres escaped en latex
		titles = [t.replace('\\&','&').replace('\\\'E','É').replace('\\`E','È').replace('\\`A','À').replace('\\OE','Œ').replace('\\^E','Ê').replace('\\oe','œ').replace('\\¨o','ö').replace('\\¨a','ä').replace('\\¨i','ï').replace('\\^i','î').replace('\\^o','ô').replace('\\¨a','ä').replace('{\\textquoteright}', '').replace('{','').replace('}','').replace('\\`e','è').replace('\\\'e','é').replace('\\`a','à').replace('\^e','ê').replace('\\guillemotright'," »").replace('\\guillemotleft',"« ").replace('\^u','û').replace('\`u','ù').replace('\^a','â') for t in titles]
		authors = [t.replace('\\&','&').replace('\\\'E','É').replace('\\`E','È').replace('\\`A','À').replace('\\OE','Œ').replace('\\^E','Ê').replace('\\oe','œ').replace('\\¨o','ö').replace('\\¨a','ä').replace('\\¨i','ï').replace('\\^i','î').replace('\\^o','ô').replace('\\¨a','ä').replace('{\\textquoteright}', '').replace('{','').replace('}','').replace('\\`e','è').replace('\\\'e','é').replace('\\`a','à').replace('\^e','ê').replace('\\guillemotright'," »").replace('\\guillemotleft',"« ").replace('\^u','û').replace('\`u','ù').replace('\^a','â') for t in authors]
		journals = [t.replace('\\&','&').replace('\\\'E','É').replace('\\`E','È').replace('\\`A','À').replace('\\OE','Œ').replace('\\^E','Ê').replace('\\oe','œ').replace('\\¨o','ö').replace('\\¨a','ä').replace('\\¨i','ï').replace('\\^i','î').replace('\\^o','ô').replace('\\¨a','ä').replace('{\\textquoteright}', '').replace('{','').replace('}','').replace('\\`e','è').replace('\\\'e','é').replace('\\`a','à').replace('\^e','ê').replace('\\guillemotright'," »").replace('\\guillemotleft',"« ").replace('\^u','û').replace('\`u','ù').replace('\^a','â') for t in journals]
	# format author field
		def format_author(authors):
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
		sep = re.compile(":|\.|\?")
		titles_short = [sep.split(title)[0] for title in titles]
		titles_short = [title[0:60] + '...' if len(title) > 60 else title for title in titles_short]

		# completions object
		completions += zip(keywords, titles, authors, years, authors_short, titles_short, journals)


	#### END COMPLETIONS HERE ####

	return completions


class PandocCiteCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		view = self.view
		point = view.sel()[0].b
		g = sublime.load_settings("PandocTools.sublime-settings")
		cite_panel_format = g.get("cite_panel_format", ["{title} ({keyword})", "{author}"])
	
		if not view.score_selector(point,"text.markdown"):
			return

		completions = get_cite_completions(view)
		#view.insert(edit, point, "@"+str(completions[1320][0]))

		def on_done(i):

			if i<0:
				return

			cite = "@" + str(completions[i][0])
			view.run_command("insert_cite",{"point":point,"ins":cite})			

		view.window().show_quick_panel([[str.format(keyword=keyword, title=title, author=author, year=year, author_short=author_short, title_short=title_short, journal=journal) for str in cite_panel_format] \
				for (keyword, title, author, year, author_short, title_short,journal) in completions], on_done)
		#view.window().show_quick_panel("123",on_done)

class InsertCiteCommand(sublime_plugin.TextCommand):
	def run(self,edit,point,ins):
		if len(self.view.sel()[0]) == 0:
			self.view.insert(edit, point,ins)
		else:
			self.view.replace(edit,self.view.sel()[0],ins)

