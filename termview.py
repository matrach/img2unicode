import os
import queue
import sys
import time
import threading
import traceback

import PIL
import numpy as np
import urwid
import urwid.raw_display
from urwid import Canvas, BoxWidget, Padding, Widget, LineBox, Filler

import img2unicode


class FSArrayCanvas(Canvas):
    def __init__(self, fsarray: 'CharsArray' = None, cursor=None):
        """
        text -- list of strings, one for each line
        attr -- list of run length encoded attributes for text
        cs -- list of run length encoded character set for text
        cursor -- (x,y) of cursor or None
        maxcol -- screen columns taken by this canvas
        check_width -- check and fix width of all lines in text
        """
        Canvas.__init__(self)

        maxcol = fsarray.width
        maxrow = fsarray.height

        self.fsarray = fsarray
        self.cursor = cursor
        self._maxcol = maxcol
        self._maxrow = maxrow

    def rows(self):
        return self._maxrow

    def cols(self):
        """Return the screen column width of this canvas."""
        return self._maxcol

    def translated_coords(self,dx,dy):
        """
        Return cursor coords shifted by (dx, dy), or None if there
        is no cursor.
        """
        if self.cursor:
            x, y = self.cursor
            return x+dx, y+dy
        return None

    def content(self, trim_left=0, trim_top=0, cols=None, rows=None,
            attr_map=None):
        """
        Return the canvas content as a list of rows where each row
        is a list of (attr, cs, text) tuples.

        trim_left, trim_top, cols, rows may be set by
        CompositeCanvas when rendering a partially obscured
        canvas.
        """
        maxcol, maxrow = self.cols(), self.rows()
        if not cols:
            cols = maxcol - trim_left
        if not rows:
            rows = maxrow - trim_top

        assert trim_left >= 0 and trim_left < maxcol
        assert cols > 0 and trim_left + cols <= maxcol
        assert trim_top >=0 and trim_top < maxrow
        assert rows > 0 and trim_top + rows <= maxrow

        # if trim_top or rows < maxrow:
        #     lines = self.fsarray[trim_top:trim_top+rows]
        # else:
        #     lines = self.fsarray
        range = self.fsarray[trim_top:trim_top+rows, trim_left:trim_left+cols]
        yield from range.render_raw()

class CharsArray:
    def __init__(self, chars, fores, backs):
        self.chars = chars
        self.fores = fores
        self.backs = backs
        self.width = chars.shape[1]
        self.height = chars.shape[0]

    def __getitem__(self, item):
        if self.fores is not None:
            return CharsArray(self.chars[item], self.fores[item], self.backs[item])
        else:
            return CharsArray(self.chars[item], self.fores, self.backs)

    def render_raw(self):
        for y in range(self.chars.shape[0]):
            line = []
            for x in range(self.chars.shape[1]):
                if self.fores is not None:
                    f = "\x1b[38;2;{};{};{}m".format(*self.fores[y, x])
                    b = "\x1b[48;2;{};{};{}m".format(*self.backs[y, x])
                    line.extend([f, b, chr(self.chars[y, x])])
                else:
                    line.append(chr(self.chars[y, x]))
            line.extend('\x1b[0m')
            yield [(None, 'U', ''.join(line).encode('utf8'))]


import logging
logging.basicConfig(filename='xxx.log', level=logging.DEBUG)

OVERDRAW = 20

class ImgWidget(Widget):
    """
    A box widget that fills an area with a single character
    """
    _sizing = frozenset(['fixed'])
    _selectable = False
    ignore_focus = True


    def __init__(self, fn: str):
        self.__super.__init__()
        self.lock = threading.RLock()
        self.img = PIL.Image.open(fn)
        logging.info("Image size %s", self.img.size)
        self.extents = 0, 0, self.img.width, self.img.height
        self.factor = max(self.img.width / (r.max_w-2*OVERDRAW), self.img.height / (r.max_h-2*OVERDRAW) / 2)
        logging.info("Initial zoom factor: %s", self.factor)
        self.extents = 0, 0, self.factor * (r.max_w-2*OVERDRAW), self.factor * (r.max_h - 2*OVERDRAW) * 2
        logging.info("Extended extents %s", self.extents)
        self.lastxy = (0, 0)
        self.invert = False
        self.show()

        self.queue = queue.Queue()
        self.thread = threading.Thread(target=self.renderer, daemon=True).start()

    def show(self, extents=None, drag_x=None, drag_y=None):
        l, u, r_, b = extents if extents is not None else self.extents
        fake_extents = -OVERDRAW*self.factor+l, -OVERDRAW*2*self.factor+u, self.factor * OVERDRAW + r_, self.factor *  2 * OVERDRAW + b
        logging.info("Fake extents: %s",fake_extents)
        img = self.img.crop(fake_extents)

        fs = CharsArray(*r.render_numpy(img, invert=self.invert))

        with self.lock:
            if extents is not None:
                self.extents = extents
                self.drag_x = drag_x
                self.drag_y = drag_y
                logging.info("New values: %s, %s, %s, last = %s", extents,
                             self.drag_x, self.drag_y, self.lastxy)

            self.fsarray = fs
            self.viewport = (slice(OVERDRAW,self.fsarray.height-OVERDRAW), slice(OVERDRAW, self.fsarray.width-OVERDRAW))
            self.viewported = self.fsarray[self.viewport]
            if self.lastxy != (0, 0):
                self.quickshow(self.lastxy[0]-self.drag_x, self.lastxy[1]-self.drag_y)
            self._invalidate()

    def renderer(self):
        while True:
            try:
                entry = self.queue.get()
                if entry is None:
                    return
                elif self.queue.qsize() > 0:
                    continue
                else:
                        logging.debug("Rendering extents: %s", entry)
                        self.show(*entry)
                        os.write(self.trigger_fd, b'\n')
            except:
                logging.critical(traceback.format_exc())
                raise

    def quickshow(self, dx, dy):
        with self.lock:
            logging.debug("Quickshow: %s, %s", dx, dy)
            if not (-OVERDRAW < dx < OVERDRAW and -OVERDRAW < dy < OVERDRAW):
                return
            self.viewport = (slice(OVERDRAW-dy, self.fsarray.height-OVERDRAW-dy), slice(OVERDRAW-dx, self.fsarray.width-OVERDRAW-dx))
            logging.debug("Viewport: %s", self.viewport)
            self.viewported = self.fsarray[self.viewport]
            self._invalidate()


    def zoom(self, factor, col, row):
        self.factor *= factor
        logging.info("New zoom factor: %s", self.factor)
        ww, wh = self.viewported.width, self.viewported.height
        l, u, r, b = self.extents
        w = r - l
        h = b - u
        w *= factor
        h *= factor
        l = l+(w/factor-w)*(col/ww)
        u = u+(h/factor-h)*(row/wh)
        self.extents = l, u, l+w, u+h

        self.show()

    def mouse_event(self, size, event, button, col, row, focus):
        logging.info("Event %s %s %s %s %s %s", size, event, button, col, row, focus)
        if event == 'mouse press':
            if button == 4:
                self.zoom(.5, col, row)
            elif button == 5:
                self.zoom(2, col, row)
            self.drag_x = col
            self.drag_y = row
            self.drag_extents = self.extents
            self.last_drag = time.time()
        elif event == 'mouse drag' or event == 'mouse release':
            with self.lock:
                dx = (col-self.drag_x)
                dxpix = dx * self.factor
                dy = (row-self.drag_y)
                dypix = dy * self.factor * 2
                if event == 'mouse drag':
                    logging.info("Skipping drag")
                    self.quickshow(dx, dy)
                    self.lastxy = col, row
                    if abs(dx) < OVERDRAW and abs(dy) < OVERDRAW:
                        return
                l, u, r, b = self.extents
                new_extents = l-dxpix, u-dypix, r-dxpix, b-dypix
                self.queue.put((new_extents, col, row))
                self.last_drag = time.time()

    def pack(self, size=None, focus=None):
        # return self.fsarray.width, self.fsarray.height
        with self.lock:
            return self.viewported.width, self.viewported.height

    def render(self, size, focus=False ):
        with self.lock:
            return FSArrayCanvas(self.viewported)

class TestImgWidget(BoxWidget):
    """
    A box widget that fills an area with a single character
    """
    _selectable = False
    ignore_focus = True

    def render(self, size, focus=False):
        logging.debug("TEST WIDGET SIZE %s F %s", size, focus)
        return FSArrayCanvas(CharsArray(np.ones((size[1], size[0]), dtype='int')*ord('/'), None, None))


def main():
    palette = [
        ('header', 'black,underline', 'light gray', 'standout,underline',
            'black,underline', '#88a'),
        ('panel', 'light gray', 'dark blue', '',
            '#ffd', '#00a'),
        ('focus', 'light gray', 'dark cyan', 'standout',
            '#ff8', '#806'),
        ]

    screen = urwid.raw_display.Screen()
    screen.set_terminal_properties(2 ** 24)
    screen.register_palette(palette)

    mode_radio_buttons = []

    def fcs(widget):
        # wrap widgets that can take focus
        return urwid.AttrMap(widget, None, 'focus')

    def on_mode_change(rb, state, renderer):
        # if this radio button is checked
        if state:
            global r
            r = renderer
            img_w.show()

    def mode_rb(text, colors, state=False):
        # mode radio buttons
        rb = urwid.RadioButton(mode_radio_buttons, text, state)
        urwid.connect_signal(rb, 'change', on_mode_change, colors)
        return fcs(rb)

    def click_exit(button):
        raise urwid.ExitMainLoop()

    def invert_checkbox(text, state=False):
        def new_state(chbx, state):
            img_w.invert = state
            img_w.show()
        chbx = urwid.CheckBox(text, state, on_state_change=new_state)
        return fcs(chbx)

    header = (
        urwid.AttrMap(urwid.Columns([
            urwid.Pile([
                mode_rb("Quad", img2unicode.Renderer(img2unicode.FastQuadDualOptimizer(), max_h=r.max_h, max_w=r.max_w, allow_upscale=True), True),
                mode_rb("Space", img2unicode.Renderer(img2unicode.SpaceDualOptimizer(), max_h=r.max_h, max_w=r.max_w, allow_upscale=True)),
                mode_rb("Half", img2unicode.Renderer(img2unicode.HalfBlockDualOptimizer(), max_h=r.max_h, max_w=r.max_w, allow_upscale=True)),
                mode_rb("Block", img2unicode.Renderer(img2unicode.FastGenericDualOptimizer('block'), max_h=r.max_h, max_w=r.max_w, allow_upscale=True)),
                urwid.Divider(),
                fcs(urwid.Button("Exit", click_exit)),
            ]),
            urwid.Pile([
                mode_rb("No-block", img2unicode.GammaRenderer(img2unicode.FastGammaOptimizer(True, 'no_block'), max_h=r.max_h, max_w=r.max_w, allow_upscale=True)),
                mode_rb("No-block BW", img2unicode.GammaRenderer(img2unicode.FastGammaOptimizer(False, 'no_block'), max_h=r.max_h, max_w=r.max_w, allow_upscale=True)),
                mode_rb("Braille Gamma", img2unicode.GammaRenderer(img2unicode.FastGammaOptimizer(True, 'braille'), max_h=r.max_h, max_w=r.max_w, allow_upscale=True)),
                mode_rb("ASCII", img2unicode.GammaRenderer(img2unicode.FastGammaOptimizer(True, 'ascii'), max_h=r.max_h, max_w=r.max_w, allow_upscale=True)),
                urwid.Divider(),
                invert_checkbox("Invert", False)
                ]),
            ]),'panel')
        )

    img_w = ImgWidget(sys.argv[1] if len(sys.argv) else 'obama.jpg')
    body = (
        Filler(LineBox(Padding(img_w, width='pack')))
    )

    lbw = urwid.Pile([('pack', header), body])

    def unhandled_input(key):
        if key in ('Q','q','esc'):
            raise urwid.ExitMainLoop()

    loop = urwid.MainLoop(lbw, screen=screen,
        unhandled_input=unhandled_input)
    trigger_fd = loop.watch_pipe(lambda *args: ...)
    img_w.trigger_fd = trigger_fd
    loop.run()

if __name__ == "__main__":
    main()
