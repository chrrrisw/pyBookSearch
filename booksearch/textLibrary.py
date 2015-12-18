
from .library import Library
from .book import Book, UNKNOWN, bkFields
from .isbnSearch import Modes

TEXT_HELP = '''
[h | help]     - show this help
[0 | q | quit] - save and exit
[s | save]     - save
[i | isbn]     - ISBN search mode (default)
[c | lccn]     - LCCN search mode
[m | manual]   - Enter book manually
'''


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
        while True:
            book = Book()
            for f in bkFields:
                entry = input('Enter {}:'.format(f[1]))
                setattr(book, f[0], entry)
            self.add_book(book)
            print(book)
            another = input('Another [Y/n]:')
            if another == 'n':
                break

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
                    self.find_book(value=command)
                else:
                    exists, book = self.isbn_exists(command)
                    if exists:
                        print(book)
                        add_again = input("### Book exists, do you want to search again?")
                        if add_again == "y":
                            self.find_book(value=command)
                    else:
                        self.find_book(value=command)

            # Ask for the next input
            try:
                command = input("Enter {}:".format(self.mode.name))
            except EOFError:
                # When using redirected input, don't bomb out on EOF
                command = 'q'
