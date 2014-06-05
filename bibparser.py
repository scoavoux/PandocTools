#!/usr/bin/python3
# -*- coding: utf-8 -*-
import sublime


def decode_latex_string(term):
    translate_table = [('{',''),
                        ('}',''),
                        ('\\&','&'),
                        ('\\\'E','É'),
                        ('\\`E','È'),
                        ('\\`A','À'),
                        ('\\OE','Œ'),
                        ('\\^E','Ê'),
                        ('\\oe','œ'),
                        ('\\¨o','ö'),
                        ('\\¨a','ä'),
                        ('\\¨i','ï'),
                        ('\\^i','î'),
                        ('\\^o','ô'),
                        ('\\¨a','ä'),
                        ('{\\textquoteright}', ''),
                        ('\\`e','è'),
                        ('\\\'e','é'),
                        ('\\`a','à'),
                        ('\^e','ê'),
                        ('\\guillemotright'," »"),
                        ('\\guillemotleft',"« "),
                        ('\^','û'),
                        ('\`','ù'),
                        ('\^a','â')]
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
            bibf = open(filename,'r',encoding='UTF-8') 
        except IOError:
            warning("Cannot open bibliography file %s !" % (filename,))
            continue

        ## lecture
        line = bibf.readline()
        while line :
            line = line.strip("\n")
            if line and line[0] == "@":
                entry_type,*key = line.strip(",").split("{")  # idiome python 3 : key vaut la liste de ce qui vient après le 1er split
                if key and not entry_type in exceptions:
                    keyword = key[0]
                    if not keyword in entries :
                        line,entry = parse_entry(bibf)
                        entries[keyword] = entry
                    else:
                        warning("Duplicate entry %s !" % (keyword,))
            else:
                line =  bibf.readline()
    return entries