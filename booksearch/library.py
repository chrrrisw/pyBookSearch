#!/usr/bin/env python3
"""Define a Library class to store a list of books."""

from .book import Book, bkFields
import csv
import sys


class Library(object):
    """The Library class is responsible for..."""

    def __init__(self, filename, delimiter='|'):
        """
        Initialise the book list to an empty list and store the filename.
        """

        self.book_list = []
        self.filename = filename
        self.delimiter = delimiter

    @property
    def book_count(self):
        return len(self.book_list)

    def isbn_exists(self, isbn):
        """
        Check for the existence of the given ISBN within the list of books.
        """

        exists = False
        book = None
        for book in self.book_list:
            if book.isbn == isbn:
                exists = True
                break
        return exists, book

    def add_book(self, book):
        """Add a book to the list managed by this Library."""
        self.book_list.append(book)

    def remove_book(self, book):
        """Remove a book from the list managed by this Library."""
        try:
            self.book_list.remove(book)
        except ValueError:
            print("### Could not remove book.")

#     def remove_isbn(self, isbn):
#         """
#         Remove all books with the given ISBN from the list
#         managed by this Library.
#         """

#         # Use a list comprehension to modify the book list
#         # http://stackoverflow.com/questions/1207406/remove-items-from-a-list-while-iterating-in-python
#         self.book_list[:] = [book for book in self.book_list if book.isbn != isbn]

# ##        for book in self.book_list:
# ##            if book.isbn == isbn:
# ##                self.remove_book(book)

    def read_from_file(self):
        """
        Open the CSV file associated with this Library, and create a
        Book for each book described within.
        """

        try:
            with open(self.filename, "rt") as library_file:

                # Detect the dialect
                try:
                    dialect = csv.Sniffer().sniff(library_file.read(2048))
                except csv.Error as e:
                    sys.exit('{}'.format(e))

                print('Detected delimiter:', dialect.delimiter)
                # print('doublequote', dialect.doublequote)
                # print('escapechar', dialect.escapechar)
                # print('lineterminator', dialect.lineterminator)
                # print('quotechar', dialect.quotechar)
                # print('quoting', dialect.quoting)
                # print('skipinitialspace', dialect.skipinitialspace)

                # Go back to start of file
                library_file.seek(0)

                # The first line of the file is to be used for key names
                book_reader = csv.DictReader(library_file, dialect=dialect)

                for book in book_reader:
                    self.book_list.append(Book(**book))

        except IOError:
            print("### No library file.")

    def save_to_file(self):
        '''
        Open the CSV file associated with this library, and write an entry
        for each book.
        '''

        with open(self.filename, "wt") as library_file:
            book_writer = csv.writer(
                library_file,
                lineterminator='\n',
                delimiter=self.delimiter)

            # Write the heading row
            book_writer.writerow([f[1] for f in bkFields])

            # Write the book data
            for book in self.book_list:
                book_writer.writerow(
                    [getattr(book, f[0]) for f in bkFields])

        print("Saved", self.filename)

if __name__ == "__main__":
    library = Library("library_test.csv")
    library.read_from_file()

    library.add_book(Book(
        isbn="1234", title="title1234", author="author1234"))
    library.add_book(Book(
        isbn="2345", title="title2345", author="author2345"))
    library.add_book(Book(
        isbn="3456", title="title3456", author="author3456"))

    # library.remove_isbn("2345")

    library.save_to_file()
