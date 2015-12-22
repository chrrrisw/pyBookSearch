#!/usr/bin/env python3

from .book import Book, UNKNOWN
import json
import sys
from enum import IntEnum

try:
    import urllib.request
    import urllib.error
    import urllib.parse
    HAVE_URLLIB = True
except ImportError:
    import urllib2
    HAVE_URLLIB = False

try:
    from bs4 import BeautifulSoup, SoupStrainer
    HAVE_SOUP = True
except ImportError:
    HAVE_SOUP = False


class Modes(IntEnum):
    ISBN = 1
    LCCN = 2


class BaseSearcher(object):
    name = ''

    def __init__(self):
        self._resolver = None

    def set_resolver(self, resolver):
        self._resolver = resolver

    def search(self, isbn, mode, book=None, fill=False):
        if book is None:
            book = Book(isbn=str(isbn))
        else:
            book.isbn = isbn
        return book


class UPCDatabaseCom(BaseSearcher):
    name = 'www.upcdatabase.com'

    def __init__(self):
        super(UPCDatabaseCom, self).__init__()
        self.search_url = 'http://www.upcdatabase.com/item/'

    def search(self, isbn, mode, book=None, fill=False):
        # Call the superclass method to create the book
        book = super(UPCDatabaseCom, self).search(
            isbn=isbn,
            mode=mode,
            book=book,
            fill=fill)
        return book


class LibraryThingCom(BaseSearcher):
    name = 'www.librarything.com'

    # The following requires a key/username
    # https://www.librarything.com/wiki/index.php/LibraryThing_JSON_Books_API
    # www.librarything.com/api_getdata.php

    # https://www.librarything.com/search.php?search=9780004704814&searchtype=media&searchtype=media&sortchoice=0
    # https://www.librarything.com/search.php?term=9780004704814

    def __init__(self):
        super(LibraryThingCom, self).__init__()
        self.search_url = 'http://www.librarything.com/tag/'

    def search(self, isbn, mode, book=None, fill=False):
        # Call the superclass method to create the book
        book = super(LibraryThingCom, self).search(
            isbn=isbn,
            mode=mode,
            book=book,
            fill=fill)
        return book


class OpenISBNCom(BaseSearcher):
    name = 'www.openisbn.com'

    def __init__(self):
        super(OpenISBNCom, self).__init__()
        self.search_url = 'http://www.openisbn.com/isbn/'
        # http://openisbn.com/isbn/0006174280/

    def search(self, isbn, mode, book=None, fill=False):
        # Call the superclass method to create the book
        book = super(OpenISBNCom, self).search(
            isbn=isbn,
            mode=mode,
            book=book,
            fill=fill)
        return book


class ISBNDBCom(BaseSearcher):
    name = 'isbndb.com'

    def __init__(self):
        super(ISBNDBCom, self).__init__()
        self.search_url = 'http://isbndb.com/api/v2/json/[your-api-key]/book/'

    def search(self, isbn, mode, book=None, fill=False):
        # Call the superclass method to create the book
        book = super(ISBNDBCom, self).search(
            isbn=isbn,
            mode=mode,
            book=book,
            fill=fill)
        return book


class ISBNPlusOrg(BaseSearcher):
    name = 'isbnplus.org'

    def __init__(self):
        super(ISBNPlusOrg, self).__init__()
        # http://isbnplus.org/api/
        self.search_url = ''

    def search(self, isbn, mode, book=None, fill=False):
        # Call the superclass method to create the book
        book = super(ISBNPlusOrg, self).search(
            isbn=isbn,
            mode=mode,
            book=book,
            fill=fill)
        return book


class OpenLibraryOrg(BaseSearcher):
    name = 'openlibrary.org'

    def __init__(self):
        super(OpenLibraryOrg, self).__init__()
        # Documentation at https://openlibrary.org/dev/docs/api/books
        self.lccn_url = 'https://openlibrary.org/api/books?bibkeys=LCCN:{}&format=json&jscmd=data'
        self.isbn_url = 'https://openlibrary.org/api/books?bibkeys=ISBN:{}&format=json&jscmd=data'

    def search(self, isbn, mode, book=None, fill=False):
        # Call the superclass method to create the book
        book = super(OpenLibraryOrg, self).search(
            isbn=isbn,
            mode=mode,
            book=book,
            fill=fill)

        if mode == Modes.ISBN:
            full_url = self.isbn_url.format(isbn)
        elif mode == Modes.LCCN:
            full_url = self.lccn_url.format(isbn)

        # Guard against URL errors
        try:

            # Open the URL
            page = urllib.request.urlopen(full_url)

            # We expect JSON data
            book_json = json.loads(page.read().decode())
            book_data = {'isbn': isbn}

            # identifiers -> {isbn_10, isbn_13, openlibrary, etc}
            # authors -> list of {name, url}
            # publish_date -> string
            # publishers -> list of {name}
            # title -> string
            # subtitle -> string

            # If there are no keys, there is no data
            if len(book_json.keys()) > 0:

                for k1 in book_json.keys():

                    # print('OpenLibraryOrg key: {}'.format(k1))

                    # Get the title and subtitle, join them
                    book_data['title'] = book_json[k1].get(
                        'title',
                        UNKNOWN)
                    subtitle = book_json[k1].get('subtitle', '')
                    if subtitle != '':
                        book_data['title'] = '{} : {}'.format(book_data['title'], subtitle)

                    # Concatenate all the authors
                    if 'authors' in book_json[k1]:
                        authors = ';'.join(
                            [a['name'] for a in book_json[k1]['authors']])
                        if authors != '':
                            book_data['author'] = authors

                    # Concatenate all the publishers
                    if 'publishers' in book_json[k1]:
                        publishers = ';'.join(
                            [p['name'] for p in book_json[k1]['publishers']])
                        if publishers != '':
                            book_data['publisher'] = publishers

                    # Get the published date
                    book_data['published'] = book_json[k1].get(
                        'publish_date',
                        UNKNOWN)

                    # Get the identifiers
                    if 'identifiers' in book_json[k1]:
                        for i in book_json[k1]['identifiers'].get('isbn_10', []):
                            book_data['isbn10'] = i
                        for i in book_json[k1]['identifiers'].get('isbn_13', []):
                            book_data['isbn13'] = i
                            if mode == Modes.LCCN:
                                book_data['isbn'] = i
                        for i in book_json[k1]['identifiers'].get('lccn', []):
                            book_data['lccn'] = i

                if fill:
                    book.update_unknowns(resolver=self._resolver, **book_data)
                else:
                    book.update(**book_data)

            else:
                print('\tISBN not found at www.openlibrary.org')
                book_data['title'] = UNKNOWN
                # book.unknown_title()

        except urllib.error.URLError as err:
            print('URLError {}'.format(err))
        except:
            print('Unexpected error:', sys.exc_info()[0])
            raise

        return book


class ISBNSearchOrg(BaseSearcher):
    name = 'www.isbnsearch.org'

    def __init__(self):
        super(ISBNSearchOrg, self).__init__()
        self.search_url = 'http://www.isbnsearch.org/isbn/'

        if HAVE_SOUP:
            # Only process the core content division
            self.bookinfo_filter = SoupStrainer('div')

    def search(self, isbn, mode, book=None, fill=False):
        # Call the superclass method to create the book
        book = super(ISBNSearchOrg, self).search(
            isbn=isbn,
            mode=mode,
            book=book,
            fill=fill)

        book_data = {'isbn': isbn}

        if HAVE_SOUP:
            full_url = self.search_url + str(isbn)
            try:
                if HAVE_URLLIB:
                    urlexception = urllib.error.URLError
                    page = urllib.request.urlopen(full_url)
                else:
                    urlexception = urllib2.URLError
                    page = urllib2.urlopen(full_url)

                soup = BeautifulSoup(
                    page.read(),
                    'html.parser',
                    parse_only=self.bookinfo_filter)

                # get the original encoding
                # original_encoding = soup.originalEncoding
                # print ('encoding: '.format(original_encoding))

                # Get the title, which may fail
                try:
                    # TODO: This is a hack for &
                    # TODO: make html/xml safe
                    book_data['title'] = soup.h2.string.replace('&', '&amp;')
                    # print ('title: {}'.format(soup.h2.string))
                except AttributeError:
                    # print('### Error retrieving Title.')
                    book_data['title'] = UNKNOWN

                if book_data['title'][:4] == 'ISBN':
                    # BOGUS TITLE
                    book_data['title'] = UNKNOWN

                # Get the remaining values
                for label in soup.find_all('strong'):

                    # ISBN-13
                    if label.string == 'ISBN-13:':
                        try:
                            book_data['isbn13'] = label.find_next_sibling('a').contents[0]
                        except AttributeError:
                            book_data['isbn13'] = UNKNOWN

                    # ISBN-10
                    if label.string == 'ISBN-10:':
                        try:
                            book_data['isbn10'] = label.find_next_sibling('a').contents[0]
                        except AttributeError:
                            book_data['isbn10'] = UNKNOWN

                    # Get the author
                    if label.string == 'Author:':
                        try:
                            # TODO: This is a hack for &
                            # TODO: make html/xml safe
                            book_data['author'] = label.nextSibling.string.replace(
                                '&', '&amp;')
                        except AttributeError:
                            book_data['author'] = UNKNOWN

                    if label.string == 'Authors:':
                        try:
                            # TODO: This is a hack for &
                            # TODO: make html/xml safe
                            book_data['author'] = label.nextSibling.replace(
                                '&', '&amp;')
                        except AttributeError:
                            book_data['author'] = UNKNOWN

                    if label.string == 'Binding:':
                        # TODO: This is a hack for &
                        book_data['binding'] = label.nextSibling.replace(
                            '&', '&amp;')

                    if label.string == 'Publisher:':
                        # TODO: This is a hack for &
                        book_data['publisher'] = label.nextSibling.replace(
                            '&', '&amp;')

                    if label.string == 'Published:':
                        # TODO: This is a hack for &
                        book_data['published'] = label.nextSibling.replace(
                            '&', '&amp;')

                # gets the first used price
                try:
                    book_data['usedPrice'] = soup.find_all('table', class_='prices')[1].tbody.tr.td.find_next_sibling(class_='price').p.a.contents
                # if there isn't a price record
                except IndexError:
                    book_data['usedPrice'] = UNKNOWN

            except urlexception as err:
                print('\tISBN not found at www.isbnsearch.org: {}'.format(
                    err.code))
                book_data['title'] = UNKNOWN
                # book.unknown_title()

        if fill:
            book.update_unknowns(resolver=self._resolver, **book_data)
        else:
            book.update(**book_data)

        return book
