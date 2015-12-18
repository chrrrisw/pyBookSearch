#!/usr/bin/env /usr/bin/python3

import sys
import argparse
import csv

from booksearch.book import Book, UNKNOWN, bkFields, FUZZ_FACTOR


def resolver(field, first, second):
    print('CONFLICT in {}'.format(field))
    print('\t1: {}'.format(first))
    print('\t2: {}'.format(second))
    number = input('Please specify your choice:')
    if number == '1':
        choice = first
    else:
        choice = second
    return choice


def read_library(filename, books, books_no_id):
    try:
        with open(filename, "rt") as library_file:

            # Detect the dialect
            try:
                dialect = csv.Sniffer().sniff(library_file.read(2048))
            except csv.Error as e:
                sys.exit('{}'.format(e))

            print('Detected delimiter:', dialect.delimiter)

            # Go back to start of file
            library_file.seek(0)

            # The first line of the file is to be used for key names
            book_reader = csv.DictReader(library_file, dialect=dialect)

            for book in book_reader:
                isbn = book['ISBN']
                new_book = Book(**book)
                if isbn in ['', 'NA', UNKNOWN]:
                    books_no_id.append(new_book)
                else:
                    if isbn in books:
                        print('\nDuplicate book found')
                        # print(books[isbn])
                        # print(new_book)
                        books[isbn].update_unknowns(resolver=resolver, **book)
                        print(books[isbn])
                    else:
                        books[isbn] = new_book

    except IOError:
        print("### No library file {}.".format(filename))


def write_library(filename, books, books_no_id):
    '''
    Open the CSV file associated with this library, and write an entry
    for each book.
    '''

    with open(filename, "wt") as library_file:
        book_writer = csv.writer(
            library_file,
            lineterminator='\n',
            delimiter='|')

        # Write the heading row
        book_writer.writerow([f[1] for f in bkFields])

        # Write the book data
        for book in books:
            book_writer.writerow(
                [getattr(books[book], f[0]) for f in bkFields])
        for book in books_no_id:
            book_writer.writerow(
                [getattr(book, f[0]) for f in bkFields])

    print("Saved", filename)


def main():
    global FUZZ_FACTOR

    FUZZ_FACTOR = 90

    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Concatenates two library files add_argument removes duplicates after
merging identical books to remove Unknown values.''',
        description='Merge two libraries')

    parser.add_argument(
        dest="outfile",
        default=None,
        help="output library file (default: %(default)s)",
        metavar="outputfile")

    parser.add_argument(
        dest="libfile1",
        default=None,
        help="first library file (default: %(default)s)",
        metavar="inputfile1")

    parser.add_argument(
        dest="libfile2",
        default=None,
        help="second library file (default: %(default)s)",
        metavar="inputfile2")

    # process options
    args = parser.parse_args()

    books_no_id = []
    books = {}

    read_library(args.libfile1, books, books_no_id)
    read_library(args.libfile2, books, books_no_id)
    write_library(args.outfile, books, books_no_id)

if __name__ == '__main__':
    main()
