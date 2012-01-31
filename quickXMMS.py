from xmmsclient import XMMS
from xmmsclient.collections import coll_parse as xmms_coll_parse
import xmmsclient
from threading import Thread
import threading
import datetime  
from time import ctime
import curses
import curses.textpad
import listbox
import string


class QuickXMMS(XMMS):

  valid_events = []
  listeners = []
  seek_amount = 5000 #TODO: Make this configurable

  def addListener(self, event, handler):
    if event not in [i['name'] for i in self.valid_events]:
      raise 'Evento "' + event + '" invalido!'
    else:
      if event not in [i['event'] for i in self.listeners]:
        for i in [i['regfun'] for i in self.valid_events 
                  if i['name'] == event]:
          i(handler)
      self.listeners.append({'event': event, 'handler:': handler})    
      return len(self.listeners) - 1

  def removeListener(self, id):
    #Not implemented, because I dont know how to 
    #cancel a broadcast registerd through the xmmsclient API
    pass
  
  def __init__(self):
    self.valid_events.append({'name': 'status_change', 
                              'regfun': self.broadcast_playback_status})
    self.valid_events.append({'name': 'song_change',
                              'regfun': self.broadcast_playback_current_id})
    #TODO: try/catch
    self.connect()

  def __sendCommand(self, command):
    command.wait()
    return command.value()

  def next(self):
    res = self.__sendCommand(self.playlist_set_next_rel(1))
    self.__sendCommand(self.playback_tickle())
    return res

  def prev(self):
    res = self.__sendCommand(self.playlist_set_next_rel(-1))
    self.__sendCommand(self.playback_tickle())
    return res

  def toggle(self):
    status = self.__sendCommand(self.playback_status())
    if (status == xmmsclient.PLAYBACK_STATUS_PLAY):
      self.__sendCommand(self.playback_pause())
    else:
      self.__sendCommand(self.playback_start())
  
  def begin_of_song(self):
    self.__sendCommand(self.playback_seek_ms(0))

  def forward(self):
    self.__sendCommand(self.playback_seek_ms_rel(self.seek_amount))

  def backward(self):
    self.__sendCommand(self.playback_seek_ms_rel(-self.seek_amount))    

  def getSongInfo(self, id):
    return self.__sendCommand(self.medialib_get_info(id))

  def getPlayTime(self):
    return self.__sendCommand(self.playback_playtime(id))

  def search(self, query, columns_to_return):
    coll = xmms_coll_parse(query)
    res = self.__sendCommand(self.coll_query_infos(coll, columns_to_return))
    res.insert(0, query)
    return res

class QuickXMMSModel:
  
  currentInfo = dict()
  currentTime = 0
  currentStatus = -1
  xmms = None

  def do_on_status_change(self, newStatus):
    self.currentStatus = newStatus.value()

  def do_on_song_change(self, newSongId):
    self.currentInfo = self.xmms.getSongInfo(newSongId.value())

  def get_artist(self):
    if 'artist' in self.currentInfo:
      return self.currentInfo['artist'].encode('utf-8')
    else:
      return ''

  def get_album(self):
    if 'album' in self.currentInfo:
      return self.currentInfo['album'].encode('utf-8')
    else:
      return ''

  def get_title(self):
    if 'title' in self.currentInfo:
      return self.currentInfo['title'].encode('utf-8')
    else:
      return ''
  
  def get_time(self):
    ms = self.xmms.getPlayTime()
    self.currentTime = datetime.time(ms / 3600000, 
                                     ms / 60000 % 60, 
                                     ms / 1000 % 60)
    return self.currentTime

  def search(self, query, result_columns):
    query = '*' + query + '*'
    return self.xmms.search(query, result_columns)

  def __init__(self):
    self.xmms = QuickXMMS()
    self.xmms.addListener("status_change", self.do_on_status_change)
    self.xmms.addListener("song_change", self.do_on_song_change)
    self.t = Thread(target=self.xmms.loop)
    self.t.daemon = True
    self.t.start()
    
commands = dict({"t": QuickXMMS.toggle,
                 "p": QuickXMMS.prev,
                 "n": QuickXMMS.next,
                 "b": QuickXMMS.backward,
                 "f": QuickXMMS.forward,
                 "a": QuickXMMS.begin_of_song})

class QuickXMMSView:
  
  win = None
  model = None #QuickXMMsModel
  t = None

  def __init__(self, scr):
    self.win = scr
    self.model = QuickXMMSModel()
    self.main_loop()


  def update(self):
    self.win.addstr(1, 1, 'PLAYER')
    self.win.addnstr(2, 1, 'Artist: ' + self.model.get_artist(), 30)
    self.win.clrtoeol()
    self.win.addstr(3, 1, 'Album: ' + self.model.get_album())
    self.win.clrtoeol()
    self.win.addstr(4, 1, 'Title: ' + self.model.get_title())
    self.win.clrtoeol()
    self.win.addstr(5, 1, self.model.get_time().isoformat())

  def execute_command(self, key):
    if key in commands:
      commands[key](self.model.xmms)
    
  def search(self):
    win_height, win_width = self.win.getmaxyx()
    curses.textpad.rectangle(self.win, 0, 0, 2, win_width - 1)
    self.win.refresh()
    win_edit = self.win.subwin(1, win_width - 2, 1, 1)
    edit = curses.textpad.Textbox(win_edit)
    lb = listbox.ListBox(self.win, 0, 3, win_height - 4, win_width)

    edit.edit()
    query = edit.gather()[:-1]
    results = self.model.search(query,
                                ['artist', 'album', 'title'])
    results.insert(0, '*' + query + '*')
    lb.items = results
    lb.refresh()
    
    while 1:
      curses.curs_set(0)
      key = self.win.getch(1, 1)
      if key > -1:
        if key == curses.KEY_UP:
          lb.scroll(-1)
        elif key == curses.KEY_DOWN:
          lb.scroll(1)
        elif key == curses.KEY_NPAGE:
          lb.scroll(3)
        elif key == curses.KEY_PPAGE:
          lb.scroll(-3)
        else:
          curses.curs_set(1)
          edit.edit()
          query = edit.gather()[:-1]
          results = self.model.search(query,
                                      ['artist', 'album', 'title'])
          results.insert(0, '*' + query + '*')
          lb.items = results
          lb.refresh()
    curses.curs_set(1)

  def main_loop(self):
    self.search()
    while 1:
      key = (self.win.getch(1, 1))
      if key > -1:
        print key
        char = chr(key)
        if key == 27:
          self.model.xmms.exit_loop()
          break
        else:
          self.execute_command(char)
      self.update()

def go():
  a = curses.initscr()
  a.nodelay(1)
  a.keypad(1)
  curses.noecho()
  try:
    QuickXMMSView(a)
  finally:
    a.nodelay(1)
    curses.echo()
    curses.endwin()
    print 'end'

a = QuickXMMS()
b = QuickXMMSModel()
go()
#print a.next()
#print a.prev()
#a.xmms.broadcast_playback_current_id(a.b_on_current_id)
#a.xmms.broadcast_playback_status(a.b_on_current_status)
#a.xmms.broadcast_playback_status(a.b_on_current_status2)
#a.xmms.broadcast_playlist_current_pos(a.b_on_current_pos)
#a.xmms.signal_playback_playtime(a.s_on_playback_playtime)
#a.xmms.broadcast_mediainfo_reader_status(a.s_on_m)
#t = Thread(target=a.xmms.loop)

print 'foi'

#ID3(urlparse.urlparse(urllib.unquote(c.replace('+', ' '))).path)
