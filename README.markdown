# franki: Field Replacement for Anki

 * populate extra fields in a deck from an external source (e.g. adding stories from revtk or ja keywords to a heisig deck)
 * bulk editing of fields (e.g. find-replace, merging/splitting)
 * update field data to a later version (e.g. collaborative sentence mining from textbooks)

franki was retrieved from the old Anki Wiki Page (ContribFugounashi). Original author is unknown.

Usage: franki options

    Options:
       --version             show program's version number and exit
       -h, --help            show this help message and exit
       -q, --quiet           don't print status messges
       -v, --verbose         print modified records


  Required Options:
    Each of the following options must be specified.

    -d DECK, --deck=DECK
                        anki deck file
    -f FILE, --file=FILE
                        replacement data file, utf-8, tab separated fields
                        numbered from 1
    -m MODEL, --model=MODEL
                        model name in DECK
    -k NAME NUMBER, --key=NAME NUMBER
                        field name NAME in DECK to be matched with field
                        number NUMBER in FILE
    -r NAME NUMBER, --replace=NAME NUMBER
                        field name NAME in DECK to be replaced with field
                        number NUMBER from FILE, can be specified multiple
                        times
