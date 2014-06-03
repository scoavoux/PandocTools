#!/usr/bin/python3
# -*- coding: utf-8 -*-

import codecs

def decode_latex_string(term):
    translate_table = [(u'{',u''),
                        (u'}',u''),
                        (u'\\&',u'&'),
                        (u'\\\'E',u'É'),
                        (u'\\`E',u'È'),
                        (u'\\`A',u'À'),
                        (u'\\OE',u'Œ'),
                        (u'\\^E',u'Ê'),
                        (u'\\oe',u'œ'),
                        (u'\\¨o',u'ö'),
                        (u'\\¨a',u'ä'),
                        (u'\\¨i',u'ï'),
                        (u'\\^i',u'î'),
                        (u'\\^o',u'ô'),
                        (u'\\¨a',u'ä'),
                        (u'{\\textquoteright}', u''),
                        (u'\\`e',u'è'),
                        (u'\\\'e',u'é'),
                        (u'\\`a',u'à'),
                        (u'\^e',u'ê'),
                        (u'\\guillemotright',u" »"),
                        (u'\\guillemotleft',u"« "),
                        (u'\^u',u'û'),
                        (u'\`u',u'ù'),
                        (u'\^a',u'â')]
    for key,val in translate_table :
        term = term.replace(key,val)
    return term

def warning(msg):
    msg = "Warning: " + msg
    print(msg)
    sublime.status_message(msg)

def parse_entry(bibf):
    entry = {}
    line =  bibf.readline()
    while line !="}\n":
        line = line.strip("\n")
        if "=" in line :
            key,value = line.split("=")
            key = key.strip("\n {},")
            value = decode_latex_string(value.strip("\n {},"))
            entry[key.lower()] = value
        line =  bibf.readline()
    return line,entry

def parse_bibtex(filenames,exceptions=[]):
    entries = {}
    for filename in filenames :
        ## Ouverture
        try:
            bibf = codecs.open(filename,'r','UTF-8',"ignore")  # 'ignore' to be safe
        except IOError:
            warning("Cannot open bibliography file %s !" % (filename,))
            continue

        ## lecture
        line = bibf.readline()
        while line :
            line = line.strip("\n")
            if line[0] == "@":
                type_and_key = line.strip(",").split("{")
                if len(type_and_key) == 2 and not type_and_key[0] in exceptions:
                    keyword = type_and_key[1]
                    if not keyword in entries :
                        line,entry = parse_entry(bibf)
                        entries[keyword] = entry
                    else:
                        warning("Duplicate entry %s !" % (keyword,))
            else:
                line =  bibf.readline()
    return entries
