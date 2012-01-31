import curses
from math import factorial
from datetime import datetime
from random import randrange
import string
from listbox import ListBox
import curses.textpad



def xla(src_win):

#    l = ListBox(src_win, 1, 1, 5, 20)
#    l.items = ['bingo', 'roleta', 'camelo', 'cavalo', 'piscina']
    
    # w1 = src_win.subwin(5, 10, 10, 15)
    # w1.border()
    # w1.refresh()
    # src_win.addstr(1, 1, str(w1.getbegyx()[1]))
    # src_win.addstr(2, 1, str(w1.getmaxyx()))

    # curses.textpad.rectangle(src_win, 1, 1, 20, 20)
    # src_win.refresh()
    #win = src_win.subwin(18, 18, 2, 2)
#    rec = curses.textpad.Textbox(win)

    # def xlanga(ll):
    #     src_win.addstr(21, 2, rec.gather())
    #     src_win.addstr(23, 4, "teste")
    #     src_win.refresh()
    #     return ll
    #     win.refresh()

 #   rec.edit()

    key = 0
    xla = []
    while key != 27:
        key = src_win.getch(0, 0)
        xla.append(key)
    return xla


import pdb
import unicodedata
import locale

def go():
    
    locale.setlocale(locale.LC_ALL, '')
  
    a = curses.initscr()
    curses.raw()
    y = []
    try:
        a.keypad(1)
#        y = xla(a)
        a.addstr(1, 0, str(a.getch(0,0)))
        a.addstr(2, 0, str(a.getch(0,0)))
        a.addstr(3, 0, str(a.getch(0,0)))
        a.addstr(4, 0, str(a.getch(0,0)))
        a.addstr(5, 0, str(a.getch(0,0)))
        a.addstr(6, 0, str(a.getch(0,0)))
        a.addstr(7, 0, str(a.getch(0,0)))
       

    finally:
        a.nodelay(1)
        curses.endwin()
        a.keypad(0)
        curses.echo()
        print y
        print 'end'
        

go()
