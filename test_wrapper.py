# -*- coding: utf-8 -*-
import bibparser

bibdata = bibparser.parse_bibtex(["/home/yate/Documents/Bibliographie/test.bib"],exceptions=["@comment","@string"])
print(bibdata)