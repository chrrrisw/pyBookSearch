#!/usr/bin/env python3

from difflib import SequenceMatcher

try:
    from fuzzywuzzy import fuzz
    HAVE_FUZZ = True
except ImportError:
    HAVE_FUZZ = False

# The order of fields in bkFields.
# WARNING: If you change this, change the list below
(
    bkISBN,
    bkISBN10,
    bkISBN13,
    bkLCCN,
    bkTitle,
    bkAuthor,
    bkBinding,
    bkPublisher,
    bkPublished,
    bkUsedPrice
) = list(range(10))

# A mapping from Book properties to CSV Column Titles.
# WARNING: If you change this, change the list above.
bkFields = [
    ('isbn', "ISBN"),
    ('isbn10', "ISBN10"),
    ('isbn13', "ISBN13"),
    ('lccn', "LCCN"),
    ('title', "Title"),
    ('author', "Author"),
    ('binding', "Binding"),
    ('publisher', "Publisher"),
    ('published', "Published"),
    ('usedPrice', "UsedPrice")
]

# The string used for unknown book fields.
UNKNOWN = 'Unknown'

# A sequence matcher from the standard library to determine if
# two conflicting book field values are worth bothering the user
# about.
SM = SequenceMatcher()

# A fuzz factor that determines the tolerance for the diff
FUZZ_FACTOR = 60


def check_and_sanitise(s):
    # TODO: Parse the input string for non-escaped html entities
    pass


class Book(object):
    '''
    A class to hold book information. The information held is based
    upon the bkFields list of tuples.
    '''

    def __init__(self, **kwargs):
        '''
        Initialise the book from the given keyword arguments
        by iterating through bkFields and looking through kwargs
        for either the property name (f[0]) or the column name (f[1]),
        with a preference for the property name. If neither are found,
        UNKNOWN is used as the default.
        '''
        self.update(**kwargs)

    def update(self, **kwargs):
        '''
        Update the book from the given keyword arguments
        by iterating through bkFields and looking through kwargs
        for either the property name (f[0]) or the column name (f[1]),
        with a preference for the property name. If neither are found,
        UNKNOWN is used as the default.
        '''
        for f in bkFields:
            setattr(
                self,
                f[0],
                kwargs.get(
                    f[0],
                    kwargs.get(
                        f[1],
                        UNKNOWN)))

    def update_unknowns(self, resolver=None, **kwargs):
        '''
        Update the book information from the given keyword arguments,
        but only if the current book information is UNKNOWN.
        '''
        global HAVE_FUZZ

        for f in bkFields:
            if getattr(self, f[0]) == UNKNOWN:
                # We have an UNKNOWN value, just update it
                setattr(
                    self,
                    f[0],
                    kwargs.get(
                        f[0],
                        kwargs.get(
                            f[1],
                            UNKNOWN)))
            else:
                # Get the new an old values, do a fuzzy comparison,
                # and resolve (or not) based on user input.

                new = kwargs.get(f[0], '')
                if isinstance(new, list):
                    new = ','.join(new)
                new = new.lower()

                old = getattr(self, f[0])
                if isinstance(old, list):
                    old = ','.join(old)
                old = old.lower()

                if new != '' and new != old:
                    if HAVE_FUZZ:
                        ratio = fuzz.ratio(new, old)
                    else:
                        SM.set_seqs(new, old)
                        ratio = int(SM.ratio() * 10)
                    if ratio < FUZZ_FACTOR:
                        if resolver is not None:
                            choice = resolver(f[0], new, old)
                            setattr(self, f[0], choice)
                        else:
                            print('Not setting different values for: {}'.format(f[0]))
                            print('\tnew:{}\n\told:{}\n\tratio:{}'.format(
                                new, old, ratio))

    def display_unknowns(self, **kwargs):
        '''
        Display the unknown fields in a book
        '''
        print("No data for:")
        for f in bkFields:
            if getattr(self, f[0]) == UNKNOWN:
                print('\t', f[0])

    # def unknown_title(self):
    #     if self.title == UNKNOWN:
    #         self.title = input('Enter Unknown title:')

    @property
    def has_unknowns(self):
        '''
        Returns True if the book has any fields matching UNKNOWN.
        '''
        for f in bkFields:
            if getattr(self, f[0]) == UNKNOWN:
                return True
        return False

    @property
    def isbn(self):
        '''
        The ISBN or LCCN used in the search.
        '''
        return self._isbn

    @isbn.setter
    def isbn(self, value):
        if value == '' or value is None:
            self._isbn = UNKNOWN
        else:
            self._isbn = value.strip()

    @property
    def isbn10(self):
        '''
        The ISBN10 value returned from the search.
        '''
        return self._isbn10

    @isbn10.setter
    def isbn10(self, value):
        if value == '' or value is None:
            self._isbn10 = UNKNOWN
        else:
            self._isbn10 = value.strip()

    @property
    def isbn13(self):
        '''
        The ISBN13 value returned from the search.
        '''
        return self._isbn13

    @isbn13.setter
    def isbn13(self, value):
        if value == '' or value is None:
            self._isbn13 = UNKNOWN
        else:
            self._isbn13 = value.strip()

    @property
    def lccn(self):
        '''
        The LCCN value returned from the search.
        '''
        return self._lccn

    @lccn.setter
    def lccn(self, value):
        if value == '' or value is None:
            self._lccn = UNKNOWN
        else:
            self._lccn = value.strip()

    @property
    def title(self):
        '''
        The Title of the book.
        '''
        return self._title

    @title.setter
    def title(self, value):
        if value == '' or value is None:
            self._title = UNKNOWN
        else:
            self._title = value.strip()

    @property
    def author(self):
        return self._author

    @author.setter
    def author(self, value):
        if value == '' or value is None:
            self._author = UNKNOWN
        else:
            self._author = value.strip()

    @property
    def binding(self):
        return self._binding

    @binding.setter
    def binding(self, value):
        if value == '' or value is None:
            self._binding = UNKNOWN
        else:
            self._binding = value.strip()

    @property
    def publisher(self):
        return self._publisher

    @publisher.setter
    def publisher(self, value):
        if value == '' or value is None:
            self._publisher = UNKNOWN
        else:
            self._publisher = value.strip()

    @property
    def published(self):
        return self._published

    @published.setter
    def published(self, value):
        if value == '' or value is None:
            self._published = UNKNOWN
        else:
            self._published = value.strip()

    @property
    def usedPrice(self):
        return self._usedPrice

    @usedPrice.setter
    def usedPrice(self, value):
        if isinstance(value, list):
            self._usedPrice = ','.join(value)
        elif value == '' or value is None:
            self._usedPrice = UNKNOWN
        else:
            self._usedPrice = value.strip()

    def __repr__(self):
        return 'Book(isbn="' + self._isbn + \
               '", title="' + self._title + \
               '", author="' + self._author + \
               '")'

    def __str__(self):
        '''
        Return a string showing all fields.
        '''
        retval = 'ISBN:' + self._isbn + '\n'
        for f in bkFields[1:]:
            retval += '\t{}: {}\n'.format(f[1], getattr(self, f[0]))
        return retval

if __name__ == "__main__":
    book = Book(
        isbn=" 0586039899 ",
        title=" The Fabulous Riverboat",
        author="  Philip Jos\u00e9 Farmer")
    print(book)
