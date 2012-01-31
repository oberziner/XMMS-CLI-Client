import curses

class ListBox:

    items = []
    left, top, height, width = 0, 0, 0, 0
    start_line = 0
    sel_item = 0
    win = None

    def __init__(self, parenwin, left , top, height, width):
        self.left = left
        self.top = top
        self.height = height
        self.width = width
        self.parenwin = parenwin
        self.lines_shown = self.height - 2
        self.win = parenwin.subwin(self.height, self.width, 
                              self.top, self.left)
        self.refresh()

    def refresh(self):
        line = 1
        cur_item = self.start_line
        while ((cur_item < len(self.items)) and (line < self.height - 1)):
            if cur_item == self.sel_item:
                attr = curses.A_STANDOUT
            else:
                attr = 0
            
            self.win.addstr(line, 1, str(self.items[cur_item]).
                            ljust(self.width - 1, chr(32)), 
                            attr)                      
            self.win.clrtoeol()
            cur_item += 1
            line += 1

        self.win.clrtobot()
        self.win.border()
        self.win.addstr(self.height -1, 2, str(self.sel_item) + ' of ' + str(len(self.items)))
        self.win.refresh()
    
    def scroll(self, lines):
        self.start_line += lines

        visible_lines = self.height - 2 # Subtract borders
        if len(self.items) - self.start_line < visible_lines:
            self.start_line = len(self.items) - visible_lines       
        if self.start_line < 0:
            self.start_line = 0
        
        self.sel_item += lines
        if self.sel_item > len(self.items) - 1:
            self.sel_item = len(self.items) -1
        if self.sel_item < 0:
            self.sel_item = 0
    
        self.refresh()
