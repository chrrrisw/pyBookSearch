from .book import Book
from gi.repository import Gtk


class GTKBookEntry(Gtk.Dialog):
    def __init__(self, parent, library=None):
        """A dialog to allow full text entry of new books."""

        print("Book Entry created")

        self.library = library

        # create dialog
        Gtk.Dialog.__init__(
            self,
            title="Add book",
            parent=parent,
            flags=Gtk.DialogFlags.DESTROY_WITH_PARENT,
            buttons=(
                Gtk.STOCK_ADD,
                Gtk.ResponseType.YES,
                Gtk.STOCK_CLOSE,
                Gtk.ResponseType.CLOSE))

        self.connect("delete-event", self.on_delete_event)
        self.add_button = self.action_area.get_children()[1]
        self.add_button.connect("clicked", self.add_callback)
        self.close_button = self.action_area.get_children()[0]
        self.close_button.connect("clicked", self.close_callback)

        self.set_border_width(5)

        box = self.get_content_area()

# ISBN

        # add a horizontal box
        hbox1 = Gtk.HBox(False, 0)
        box.pack_start(hbox1, expand=False, fill=False, padding=0)

        # add a label
        label1 = Gtk.Label("ISBN:")
        hbox1.pack_start(label1, expand=False, fill=False, padding=0)

        # add a text entry field
        self.isbn_entry = Gtk.Entry(max_length=0)
        self.isbn_entry.connect(
            "activate", self.isbn_enter_callback, self.isbn_entry)
        hbox1.pack_start(self.isbn_entry, expand=True, fill=True, padding=0)

# TITLE

        # add a horizontal box
        hbox2 = Gtk.HBox(False, 0)
        box.pack_start(hbox2, expand=False, fill=False, padding=0)

        # add a label
        label2 = Gtk.Label("Title:")
        hbox2.pack_start(label2, expand=False, fill=False, padding=0)

        # add a text entry field
        self.title_entry = Gtk.Entry(max_length=0)
        self.title_entry.connect(
            "activate", self.title_enter_callback, self.title_entry)
        hbox2.pack_start(self.title_entry, expand=True, fill=True, padding=0)

# AUTHORS

        # add a horizontal box
        hbox3 = Gtk.HBox(False, 0)
        box.pack_start(hbox3, expand=False, fill=False, padding=0)

        # add a label
        label3 = Gtk.Label("Authors:")
        hbox3.pack_start(label3, expand=False, fill=False, padding=0)

        # add a text entry field
        self.author_entry = Gtk.Entry(max_length=0)
        self.author_entry.connect(
            "activate", self.author_enter_callback, self.author_entry)
        hbox3.pack_start(self.author_entry, expand=True, fill=True, padding=0)

        # show stuff
        self.show_all()

    def isbn_enter_callback(self, widget, data=None):
        self.title_entry.grab_focus()

    def title_enter_callback(self, widget, data=None):
        self.author_entry.grab_focus()

    def author_enter_callback(self, widget, data=None):
        self.add_button.grab_focus()

    def add_callback(self, widget, data=None):
        print ("Add")
        if self.library is not None:
            book = Book(
                isbn=self.isbn_entry.get_text(),
                title=self.title_entry.get_text(),
                author=self.author_entry.get_text())
            self.library.add_book(book)
        self.isbn_entry.grab_focus()

    def close_callback(self, widget, data=None):
        print ("Close")
        self.hide()

    def on_delete_event(self, widget, data=None):
        return self.hide_on_delete()

    def destroy(self, widget, data=None):
        Gtk.main_quit()

