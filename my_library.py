#!/usr/bin/env /usr/bin/python3

import sys
import os
import argparse

try:
    from gi.repository import Gtk
    from  booksearch.gtkLibrary import GTKLibrary
    HAVE_GTK = True
except ImportError:
    print("### No GTK - reverting to text mode")
    HAVE_GTK = False

from booksearch.book import Book, UNKNOWN
from booksearch.library import Library
from booksearch.isbnSearch import Modes, ISBNSearchOrg, OpenLibraryOrg

# ==========================

__all__ = []
__version__ = 0.2
__date__ = '2015-12-10'
__updated__ = '2015-12-10'


TEXT_HELP = '''
[h | help]     - show this help
[0 | q | quit] - save and exit
[s | save]     - save
[i | isbn]     - ISBN search mode (default)
[c | lccn]     - LCCN search mode
[m | manual]   - Enter book manually
'''


def text_resolver(field, first, second):
    print('CONFLICT in {}'.format(field))
    print('\t1: {}'.format(first))
    print('\t2: {}'.format(second))
    number = input('Please specify your choice:')
    if number == '1':
        return first
    else:
        return second


class TextLibrary(Library):
    def __init__(
            self,
            filename,
            searchers=None,
            mode=Modes.ISBN,
            delimiter='|',
            fill=False,
            noquestions=False):

        self.searchers = searchers
        self.mode = mode
        self.fill = fill
        self.noquestions = noquestions

        # create library
        Library.__init__(
            self,
            filename=filename,
            delimiter=delimiter)

        # fill the model from file
        self.read_from_file()

        print('You have {} books in your library.'.format(self.book_count))

    def manual_entry_loop(self):
        print('Sorry - not yet implemented')

    def find_book(self, value):

        # Create an empty book
        book = Book(isbn=value)

        # Iterate through the searchers for the mode
        for searcher in self.searchers[self.mode]:

            print("Checking for the {} at {}... ".format(
                self.mode.name, searcher.name))

            book = searcher.search(
                isbn=value,
                mode=self.mode,
                book=book,
                fill=self.fill)

            if book.has_unknowns:
                book.display_unknowns()

            if book.author != UNKNOWN and not self.fill:
                break
            elif book.has_unknowns and self.fill:
                print("\tAttempting to fill unknown values...")
            else:
                print('\tNot found')

        if book.title == UNKNOWN and not self.noquestions:
            book.title = input('Enter Unknown title:')

        self.add_book(book)
        print(book)

    def isbn_loop(self):
        print(TEXT_HELP)
        try:
            command = input("Enter {}:".format(self.mode.name))
        except EOFError:
            # When using redirected input, don't bomb out on EOF
            command = 'q'

        while (command != '0') and (command != 'q') and (command != 'quit'):
            if command == "save" or command == 's':
                self.save_to_file()
            elif command == 'help' or command == 'h':
                print(TEXT_HELP)
            elif command == 'isbn' or command == 'i':
                self.mode = Modes.ISBN
                print("Searching by {}".format(self.mode.name))
            elif command == 'lccn' or command == 'c':
                self.mode = Modes.LCCN
                print('Searching by {}'.format(self.mode.name))
            elif command == 'manual' or command == 'm':
                print('Entering books manually')
                self.manual_entry_loop()
            else:
                # TODO:
                if self.noquestions:
                    self.find_book(command)
                else:
                    exists, book = self.isbn_exists(command)
                    if exists:
                        print(book)
                        add_again = input("### Book exists, do you want to search again?")
                        if add_again == "y":
                            self.find_book(command)
                    else:
                        self.find_book(command)

            # Ask for the next input
            try:
                command = input("Enter {}:".format(self.mode.name))
            except EOFError:
                # When using redirected input, don't bomb out on EOF
                command = 'q'


def main(argv=None):
    '''Command line options.'''

    global HAVE_GTK

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
            HAVE_GTK = False

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

    if HAVE_GTK:
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
