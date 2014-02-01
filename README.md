Very basic and messy set of tools for writing Pandoc Markdown in Sublime Text 3.

For now, PandocTools has :

* A custom syntax called PandocMarkdown that highlights many things, including YAML metadata, citation, footnotes/note call, etc.
* A pandoc_cite commands that searches a bib file for a reference and adds that reference bibtex key in a @bibtex_key format in the document. 

pandoc_cite needs at least one bibtex file in input. Add yours as 	
	"bibfiles": ["/path/to/bib/file.bib"]
In PandocTools.sublime-settings

pandoc_cite's default shortcut is "ctrl+<", which I find useful on French keyboard. It can be changed in PandocTools.sublime-keymap

Substanstial parts of the code have been adapted from [LatexTools](https://github.com/SublimeText/LaTeXTools) (for the citation) and [PandocAcademic](https://github.com/larlequin/PandocAcademic) (for the syntax).