#! /usr/bin/python
# -*- coding: utf-8 -*-

import re
import os
import sys
import errno
import codecs
import locale
import optparse
sys.path.append("/usr/share/anki") # debian libanki
sys.path.append("c:\Program Files\Anki\lib") # windows libanki and deps
sys.path.append("c:\Program Files\Anki\lib\shared.zip") # windows libanki and deps
import anki

locale.setlocale(locale.LC_ALL, "")
code=locale.getpreferredencoding()

version="franki-" + "20110428" + " libanki-" + anki.version
parser = optparse.OptionParser(usage="usage: %prog options\n-h for help", version=version)
parser.add_option("-q", "--quiet", dest="quiet", action="store_true", default=False,
 help="don't print status messges")
parser.add_option("-v", "--verbose", dest="verbose", action="store_true", default=False,
 help="print modified records")
group = optparse.OptionGroup(parser, "Required Options","Each of the following options must be specified.")
group.add_option("-d", "--deck", dest="deck", help="anki deck file", metavar="DECK")
group.add_option("-f", "--file", dest="file", help="replacement data file, utf-8, tab separated fields numbered from 1", metavar="FILE")
group.add_option("-m", "--model", dest="model", help="model name in DECK", metavar="MODEL")
group.add_option("-k", "--key", dest="key", nargs=2, 
                  help="field name NAME in DECK to be matched with field number NUMBER in FILE", metavar="NAME NUMBER")
group.add_option("-r", "--replace", dest="replace", action="append", nargs=2,
                  help="field name NAME in DECK to be replaced with field number NUMBER from FILE, can be specified multiple times", metavar="NAME NUMBER")
parser.add_option_group(group)
(options, args) = parser.parse_args()
if not options.deck or not options.file or not options.model or not options.key or not options.replace:
    parser.error("missing required option")
keyname=options.key[0]
keynum=int(options.key[1]) - 1
replace={}
for (name,num) in options.replace:
    replace[name]=int(num) - 1

data={}
file=codecs.open(options.file, "r", encoding="utf-8")
if not options.quiet: print "reading data from", options.file
for line in file:
    fields=line.split("\t")
    try:
        key=fields[keynum]
    except IndexError:
        print "no key field number '" + options.key[1] + "' in file"
        file.close()
        sys.exit(errno.EINVAL)
    if key in data:
        print "skipping line with duplicate key in file"
        continue
    data[key]={}
    for name in replace:
        try:
            data[key][name]=fields[replace[name]]
        except IndexError:
            print "no field number '" + str(replace[name] + 1) + "' in file"
            file.close()
            sys.exit(errno.EINVAL)
file.close()
if not options.quiet: print "read", len(data), "records"

fieldcount=0
if not os.path.exists(options.deck):
    print "deck", options.deck, "does not exist"
    sys.exit(errno.ENOENT)
if not options.quiet: print "replacing fields in", options.deck 
deck=anki.DeckStorage.Deck(options.deck)
modelid=deck.s.scalar("select id from models where name = '%s'" % options.model)
if not modelid:
    print "no model '" + options.model + "' in deck"
    deck.close()
    sys.exit(errno.EINVAL)
cardmodelid=deck.s.scalar("select id from cardmodels where modelId = %s" % modelid)
ids=[]
for card in deck.s.query(anki.cards.Card).filter("cardModelId = %s" % cardmodelid):
    try:
        key=card.fact[keyname]
    except KeyError:
        print "no key field name '" + keyname + "' in model"
        deck.close()
        sys.exit(errno.EINVAL)
    modified=False
    if key in data:
        for name in replace:
            try:
                if card.fact[name] != data[key][name]:
                    if options.verbose:
                        print "'" + key + "'", name, "'" + (card.fact[name]).encode(code) + "'", "'" + (data[key][name]).encode(code) + "'"
                    card.fact[name] = data[key][name]
                    fieldcount+=1
                    modified=True
            except KeyError:
                print "no field name '" + name + "' in model"
                deck.close()
                sys.exit(errno.EINVAL)
    if modified:
        ids.append(card.fact.id)
if not options.quiet: print "replaced", fieldcount, "fields in", len(ids), "cards" 
if not options.quiet: print "updating qa cache"
deck.updateCardQACacheFromIds(ids, type="facts")
if not options.quiet: print "saving"
deck.save()
deck.close()
