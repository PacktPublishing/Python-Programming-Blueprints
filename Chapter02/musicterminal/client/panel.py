import curses
import curses.panel
from uuid import uuid1


class Panel:

    def __init__(self, title, dimensions):
        height, width, y, x = dimensions

        self._win = curses.newwin(height, width, y, x)
        self._win.box()
        self._panel = curses.panel.new_panel(self._win)
        self.title = title
        self._id = uuid1()

        self._set_title()

        self.hide()

    def hide(self):
        self._panel.hide()

    def _set_title(self):
        formatted_title = f' {self.title} '
        self._win.addstr(0, 2, formatted_title, curses.A_REVERSE)

    def show(self):
        self._win.clear()
        self._win.box()
        self._set_title()
        curses.curs_set(0)
        self._panel.show()

    def is_visible(self):
        return not self._panel.hidden()

    def __eq__(self, other):
        return self._id == other._id

