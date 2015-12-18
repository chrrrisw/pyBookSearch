#!/usr/bin/env python3

from gi.repository import Gtk


class GTKScannerEntry(Gtk.Dialog):

    def __init__(self, parent, library=None):
        """"""

        self.library_page = library

        # create Dialog
        Gtk.Dialog.__init__(
            self,
            title="Enter ISBN",
            parent=parent,
            flags=Gtk.DialogFlags.DESTROY_WITH_PARENT,
            buttons=(Gtk.STOCK_CLOSE, Gtk.ResponseType.CLOSE))
        self.connect("delete-event", self.on_delete_event)
        self.close_button = self.action_area.get_children()[0]
        self.close_button.connect("clicked", self.close_callback)

        self.set_border_width(5)

        box = self.get_content_area()

        # add a label
        label1 = Gtk.Label("Enter ISBN:")
        box.pack_start(
            label1, expand=False, fill=False, padding=0)

        # add a text entry field
        self.isbn_entry = Gtk.Entry(max_length=0)
        self.isbn_entry.connect(
            "activate", self.isbn_enter_callback, self.isbn_entry)
        box.pack_start(
            self.isbn_entry, expand=False, fill=False, padding=0)

        # show stuff
        self.show_all()

    def isbn_enter_callback(self, widget, entry):
        """
        Query the web searchers for the ISBN, add the book to the
        library, clear the text field.
        """

        isbn_text = entry.get_text()

        if self.library_page is not None:
            print("ISBN exists:", self.library_page.isbn_exists(isbn_text)[0])
            self.library_page.search_isbn(isbn_text)

        entry.set_text("")

    def close_callback(self, widget, data=None):
        print("Close")
        self.hide()

    def on_delete_event(self, widget, data=None):
        return self.hide_on_delete()


if __name__ == "__main__":
    scanner_entry = GTKScannerEntry()
    Gtk.main()
