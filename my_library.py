#!/usr/bin/env /usr/bin/python3

import sys
import os
import argparse

try:
    from gi.repository import Gtk
    from booksearch.gtkLibrary import GTKLibrary
    USE_GTK = True
except ImportError:
    print("### No GTK - reverting to text mode")
    USE_GTK = False

from booksearch.isbnSearch import Modes, ISBNSearchOrg, OpenLibraryOrg
from booksearch.textLibrary import TextLibrary

# ==========================

__all__ = []
__version__ = 0.2
__date__ = '2015-12-10'
__updated__ = '2015-12-10'


def text_resolver(field, first, second):
    print('CONFLICT in {}'.format(field))
    print('\t1: {}'.format(first))
    print('\t2: {}'.format(second))
    number = input('Please specify your choice:')
    if number == '1':
        return first
    else:
        return second


def main(argv=None):
    '''Command line options.'''

    global USE_GTK

    program_name = os.path.basename(sys.argv[0])
    program_version = "v%1.2f" % __version__
    program_build_date = "%s" % __updated__

    program_desc = '''Search for book information by ISBN and add to a library CSV file.'''

    program_epilog = """{} {} ({})
Copyright 2013, 2014, 2015 Chris Willoughby and contributors
Licensed under the Apache License 2.0
http://www.apache.org/licenses/LICENSE-2.0""".format(
        program_name, program_version, program_build_date)

    try:
        # setup argument parser
        parser = argparse.ArgumentParser(
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog=program_epilog,
            description=program_desc)

        parser.add_argument(
            "-l", "--library",
            dest="libfile",
            default='auto_library.csv',
            help="set library file path (default: %(default)s)",
            metavar="FILE")
        parser.add_argument(
            "-t", "--text",
            action="store_true",
            dest="textmode",
            default=False,
            help="use text mode (default: %(default)s)")
        parser.add_argument(
            "-d", "--delimit",
            dest="delimiter",
            default="|",
            help="set the CSV delimiter (default: %(default)s)")
        parser.add_argument(
            "-f", "--fill",
            action="store_true",
            dest="fill",
            default=False,
            help="automatically fill missing details from multiple sources (default: %(default)s)")
        parser.add_argument(
            "-r", "--requery",
            action="store_true",
            dest="requery",
            default=False,
            help="automatically requery the entire library file, filling in missing details (default: %(default)s)")
        parser.add_argument(
            "-n", "--no-questions",
            action="store_true",
            dest="noquestions",
            default=False,
            help="just do it (default: %(default)s)")

        # process options
        args = parser.parse_args()

        if args.libfile:
            print("Library File: {}".format(args.libfile))

        print("Text mode:", args.textmode)
        if args.textmode:
            USE_GTK = False

        if args.delimiter:
            print("Delimiter: {}".format(args.delimiter))

        print("Fill mode:", args.fill)
        print("Re-query:", args.requery)
        print("No-questions:", args.noquestions)

    except Exception as e:
        indent = len(program_name) * " "
        sys.stderr.write(program_name + ": " + repr(e) + "\n")
        sys.stderr.write(indent + "  for help use --help\n")
        return 2

    # Create some searcher objects
    isbnSearchOrg = ISBNSearchOrg()
    openLibraryOrg = OpenLibraryOrg()

    # Put them in lists for ordered processing
    searchers = {
        Modes.ISBN: [isbnSearchOrg, openLibraryOrg],
        Modes.LCCN: [openLibraryOrg]
    }

    if USE_GTK:
        library = GTKLibrary(
            filename=args.libfile,
            searchers=searchers,
            delimiter=args.delimiter)
        Gtk.main()
    else:
        if not args.noquestions:
            isbnSearchOrg.set_resolver(text_resolver)
            openLibraryOrg.set_resolver(text_resolver)

        library = TextLibrary(
            filename=args.libfile,
            searchers=searchers,
            delimiter=args.delimiter,
            fill=args.fill,
            noquestions=args.noquestions)
        library.isbn_loop()

        # Save before exiting
        library.save_to_file()

if __name__ == "__main__":
    sys.exit(main())
