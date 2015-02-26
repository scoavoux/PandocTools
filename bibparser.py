#!/usr/bin/python3
# -*- coding: utf-8 -*-

from . import warning

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

def parse_entry(bibf):
    entry = {}
    line =  bibf.readline()
    while line and line !="}\n" :
        line = line.strip("\n")
        if "=" in line :
            key,*value = line.split("=")    
            # utiliser *value permet d'éviter de planter quand on a des entrées contenant "=".
            # Seul le premier "=" sera pris en compte
            key = key.strip("\t\n {},")
            # Transformation de la liste value en chaîne, nettoyage et décodage latex
            value = decode_latex_string(" ".join(value).strip("\t\n {},"))
            entry[key.lower()] = value
        line =  bibf.readline()
    return line,entry

def parse_bibtex(filenames,exceptions=["@comment"]):
    entries = {}
    for filename in filenames :
        ## Ouverture
        try:
            bibf = open(filename,'r',encoding='UTF-8') 
        except IOError:
            #print("Cannot open bibliography file %s !" % (filename,))             # Décommenter pour les tests
            warning.warning("Cannot open bibliography file %s !" % (filename,)) # Commenter pour les tests

        ## lecture
        line = bibf.readline()
        while line :
            line = line.strip("\n")
            if line and line[0] == "@" and line[-1] != "}":
                entry_type,*key = line.strip(",}").split("{")  # idiome python 3 : key vaut la liste de ce qui vient après le 1er split
                if key and not entry_type in exceptions:
                    # print("enter")
                    keyword = key[0].strip()
                    if not keyword in entries :
                        line,entry = parse_entry(bibf)
                        entries[keyword] = entry
                    else:
                        #print("Duplicate entry %s !" % (keyword,))             # Décommenter pour les tests
                        warning.warning("Duplicate entry %s !" % (keyword,)) # Commenter pour les tests
                        break
                else:
                    line =  bibf.readline()
            else:
                line =  bibf.readline()
    return entries
