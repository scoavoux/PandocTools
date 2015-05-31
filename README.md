PandocTools is a Sublime Text 3 package designed for academic writing in pandoc-flavoured markdown.

For now, its main features are :

+ A custom syntax that distinguishes unique pandoc features (such as citations)
+ A command that allows searching a bibtex file for references and inserting a key in the @bibtex_key format
+ A similar command for crossreferences (based on [pandoc-crossref](https://github.com/lierdakil/pandoc-crossref))
+ Autopairing of `*` and `_`
+ Auto-continuation of lists and blockquotes
+ Snippets to insert images and notes

`pandoc_cite` needs at least one bibtex file in input. Add yours as 	
	"bibfiles": ["/path/to/bib/file.bib"]
In `PandocTools.sublime-settings` in your User directory.

pandoc_cite's default shortcut is "ctrl+<". It can be changed in `Default.sublime-keymap`.

PandocTools started as an adaptation of [LatexTools](https://github.com/SublimeText/LaTeXTools) for the Pandoc Markdown syntax. Parts of the code have been adapted from [LatexTools](https://github.com/SublimeText/LaTeXTools) (for the citation) and [PandocAcademic](https://github.com/larlequin/PandocAcademic) (for the syntax).