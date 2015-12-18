#!/usr/bin/env python3

from .book import Book, bkFields, UNKNOWN, bkISBN, bkAuthor, bkTitle
from .library import Library
from gi.repository import Gtk, GObject
from .gtkScannerEntry import GTKScannerEntry
from .gtkBookEntry import GTKBookEntry
from .isbnSearch import Modes

(
    COLUMN_ISBN,
    COLUMN_AUTHOR,
    COLUMN_TITLE,
    COLUMN_REFERENCE
) = list(range(4))

MENU_INFO = """
<ui>
  <menubar name='Book'>
    <menu action='BookMenu'>
      <menuitem action='BookAdd' />
      <menuitem action='BookSearch' />
    </menu>
    <menu action='LibraryMenu'>
      <menuitem action='ExportXML'/>
    </menu>
  </menubar>
</ui>
"""

HIGHLIGHT = "<span background='yellow' foreground='black'>{}</span>"


class GTKLibrary(Gtk.Window, Library):
    def __init__(
            self,
            filename,
            searchers=None,
            mode=Modes.ISBN,
            parent=None,
            delimiter='|'):

        """Create a window with a list and a couple of buttons."""

        self.searchers = searchers
        self.search_mode = mode

        # create window
        Gtk.Window.__init__(self)

        # create library
        Library.__init__(
            self,
            filename=filename,
            delimiter=delimiter)

        try:
            self.set_screen(parent.get_screen())
            self.connect("destroy", parent.destroy)
        except AttributeError:
            self.connect("destroy", self.destroy)

        self.set_title("Books in Library")
        self.set_border_width(5)
        self.set_default_size(700, 300)

        vbox1 = Gtk.VBox(False, 4)
        self.add(vbox1)

        self.__add_menu(vbox1)

        sw = Gtk.ScrolledWindow()
        sw.set_shadow_type(Gtk.ShadowType.ETCHED_IN)
        sw.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        vbox1.pack_start(sw, expand=True, fill=True, padding=0)

        # create book model
        self.book_model = Gtk.ListStore(
            GObject.TYPE_STRING,
            GObject.TYPE_STRING,
            GObject.TYPE_STRING,
            GObject.TYPE_PYOBJECT)

        # fill the model from file
        self.read_from_file()

        # add columns to the tree view
        self.__add_tree()

        sw.add(self.tree_view)

        # add a horizontal box
        hbox1 = Gtk.HBox(False, 0)
        vbox1.pack_start(
            hbox1, expand=False, fill=False, padding=0)

        # add a query button
        self.query_button = Gtk.Button("Query")
        self.query_button.connect("clicked", self.on_query_callback, None)
        hbox1.pack_start(
            self.query_button, expand=True, fill=True, padding=0)

        # add a save button
        self.save_button = Gtk.Button("Save")
        self.save_button.connect("clicked", self.on_save_callback, None)
        hbox1.pack_start(
            self.save_button, expand=True, fill=True, padding=0)

        # add a delete button
        self.delete_button = Gtk.Button("Delete")
        self.delete_button.connect("clicked", self.on_delete_callback, None)
        hbox1.pack_start(
            self.delete_button, expand=True, fill=True, padding=0)

        self.scannerEntry = None
        self.bookEntry = None

        # show stuff
        self.show_all()

    def __add_menu(self, box):
        """Create the menus."""

        uimanager = Gtk.UIManager()
        uimanager.add_ui_from_string(MENU_INFO)

        accelgroup = uimanager.get_accel_group()
        self.add_accel_group(accelgroup)

        action_group = Gtk.ActionGroup("book_actions")

        action_book_menu = Gtk.Action("BookMenu", "Book", None, None)
        action_group.add_action(action_book_menu)

        action_book_add = Gtk.Action("BookAdd", "Add", None, Gtk.STOCK_ADD)
        action_book_add.connect("activate", self.on_menu_book_add, None)
        action_group.add_action(action_book_add)

        action_book_search = Gtk.Action(
            "BookSearch", "Search", None, Gtk.STOCK_FIND)
        action_book_search.connect("activate", self.on_menu_book_search, None)
        action_group.add_action(action_book_search)

        uimanager.insert_action_group(action_group)

        # LIBRARY MENU

        action_group = Gtk.ActionGroup("library_actions")

        action_library_menu = Gtk.Action("LibraryMenu", "Library", None, None)
        action_group.add_action(action_library_menu)

        action_library_xml = Gtk.Action(
            'ExportXML', 'Export to XML', None, Gtk.STOCK_SAVE_AS)
        action_group.add_action(action_library_xml)

        uimanager.insert_action_group(action_group)

        menubar = uimanager.get_widget("/Book")
        box.pack_start(menubar, expand=False, fill=False, padding=0)

        # mb = Gtk.MenuBar()
        # box.pack_start(mb, expand=False, fill=False, padding=0)

        # mi1 = Gtk.MenuItem("_Book")
        # mb.append(mi1)

        # m1 = Gtk.Menu()

    def __add_tree(self):
        """Create the tree."""

        # create tree view
        self.tree_view = Gtk.TreeView(self.book_model)
        # hint across rows
        self.tree_view.set_rules_hint(True)
        #
        self.tree_view.set_search_column(COLUMN_ISBN)

        # column for ISBN
        renderer = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn(
            bkFields[bkISBN][1], renderer, text=COLUMN_ISBN)
        column.set_sort_column_id(COLUMN_ISBN)
        column.set_sizing(Gtk.TreeViewColumnSizing.FIXED)
        column.set_resizable(True)
        column.set_min_width(120)
        self.tree_view.append_column(column)

        # column for author
        renderer = Gtk.CellRendererText()
        renderer.set_property("editable", True)
        column = Gtk.TreeViewColumn(
            bkFields[bkAuthor][1], renderer, markup=COLUMN_AUTHOR)
        column.set_sort_column_id(COLUMN_AUTHOR)
        column.set_sizing(Gtk.TreeViewColumnSizing.FIXED)
        column.set_resizable(True)
        column.set_min_width(150)
        self.tree_view.append_column(column)
        renderer.connect("edited", self.on_author_edited, None)

        # column for title
        renderer = Gtk.CellRendererText()
        renderer.set_property("editable", True)
        column = Gtk.TreeViewColumn(
            bkFields[bkTitle][1], renderer, markup=COLUMN_TITLE)
        column.set_sort_column_id(COLUMN_TITLE)
        column.set_sizing(Gtk.TreeViewColumnSizing.FIXED)
        column.set_resizable(True)
        column.set_min_width(150)
        self.tree_view.append_column(column)
        renderer.connect("edited", self.on_title_edited, None)

        select = self.tree_view.get_selection()
        select.connect("changed", self.on_selection_changed, None)

    def __add_dialogs(self):
        pass

    # ============ CALLBACKS

    def on_title_edited(self, widget, path, text, user_data):
        """Called when the user edits a title, updates the book."""
        if self.book_model[path][COLUMN_TITLE] != text:
            book = self.book_model[path][COLUMN_REFERENCE]
            print('Title From: {}'.format(book))
            book.title = text
            print('Title To  : {}'.format(book))

            # Do this last - if the column is sorted the path
            # points to the wrong entry
            self.book_model[path][COLUMN_TITLE] = text

    def on_author_edited(self, widget, path, text, user_data):
        """Called when the user edits a author, updates the book."""
        if self.book_model[path][COLUMN_AUTHOR] != text:
            book = self.book_model[path][COLUMN_REFERENCE]
            print('Author From: {}'.format(book))
            book.author = text
            print('Author To  : {}'.format(book))

            # Do this last - if the column is sorted the path
            # points to the wrong entry
            self.book_model[path][COLUMN_AUTHOR] = text

    def on_selection_changed(self, selection, data=None):
        model, treeiter = selection.get_selected()
        if treeiter is not None:
            print("Selected: {}".format(model[treeiter][COLUMN_REFERENCE]))

    def on_menu_book_add(self, widget, data=None):
        print("Book Add")
        if self.bookEntry is None:
            self.bookEntry = GTKBookEntry(parent=self, library=self)
        else:
            self.bookEntry.present()

    def on_menu_book_search(self, widget, data=None):
        print("Book Search")
        if self.scannerEntry is None:
            self.scannerEntry = GTKScannerEntry(library=self, parent=self)
        else:
            self.scannerEntry.present()

    def on_query_callback(self, widget, data=None):
        """Called from the query button, attempts to update data from web."""
        selection = self.tree_view.get_selection()
        (model, treeiter) = selection.get_selected()
        isbn = model.get(treeiter, 0)[COLUMN_ISBN]
        print("querying %s" % (isbn))
        self.search_isbn(isbn, add=False)

    def on_save_callback(self, widget, data=None):
        '''
        Called from various save buttons, saves the CSV file.
        '''
        print('Saving...', end=' ')
        self.save_to_file()

    def on_delete_callback(self, widget, data=None):
        '''
        '''
        print('Delete')
        selection = self.tree_view.get_selection()
        model, treeiter = selection.get_selected()
        book = model[treeiter][COLUMN_REFERENCE]
        self.remove_book(book)
        model.remove(treeiter)

    def destroy(self, widget, data=None):
        '''
        Called on closing the window, saves the CSV file.
        '''
        print('Saving...', end=' ')
        self.save_to_file()
        Gtk.main_quit()

    def set_mode(self, mode):
        self.search_mode = mode

    def add_web_searcher(self, searcher, mode):
        self.searchers[mode].append(searcher)

    def search_isbn(self, isbn, add=True):
        book = None

        for searcher in self.searchers[self.search_mode]:
            book = searcher.search(
                isbn=isbn,
                mode=self.search_mode,
                book=book)
            print(book)
            if add:
                self.add_book(book)

        if book is None and add:
            self.add_book(
                Book(isbn=isbn))

    def add_book(self, book):
        # Call the super class function
        super(GTKLibrary, self).add_book(book)

        # Add it to the model
        iter = self.book_model.append()
        self.book_model.set(
            iter,
            COLUMN_ISBN, book.isbn,
            COLUMN_TITLE, book.title,
            COLUMN_AUTHOR, book.author,
            COLUMN_REFERENCE, book)

        self.tree_view.scroll_to_cell(
            path=self.book_model.get_path(iter),
            use_align=True)

    # def remove_book(self, book):
    #     super(GTKLibrary, self).remove_book(book)

    # def remove_isbn(self, isbn):
    #     super(GTKLibrary, self).remove_isbn(isbn)

    def read_from_file(self):
        # Call the super class function
        super(GTKLibrary, self).read_from_file()

        for book in self.book_list:
            iter = self.book_model.append()

            title = book.title
            if title == UNKNOWN:
                title = HIGHLIGHT.format(title)

            author = book.author
            if author == UNKNOWN:
                author = HIGHLIGHT.format(author)

            self.book_model.set(
                iter,
                COLUMN_ISBN, book.isbn,
                COLUMN_TITLE, title,
                COLUMN_AUTHOR, author,
                COLUMN_REFERENCE, book)

if __name__ == "__main__":
    gtkLibrary = GTKLibrary("library.csv")
    gtkLibrary.add_book(Book(isbn="9876", title="9876", author="9876"))
    Gtk.main()
