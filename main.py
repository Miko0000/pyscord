#!/bin/python3

import curses
screen = curses.initscr()
curses.start_color()
curses.use_default_colors()
curses.noecho()
curses.cbreak()
curses.curs_set(0)

screen.nodelay(1)
screen.keypad(True)

import pyska
import events

cycle_count = 0;
def cycle(entity, iface):
	global cycle_count; cycle_count += 1
	if events.now(entity, iface) > 0:
		return 1

	return 0

code = 0
iface = pyska.iface(screen)
while True:
	code = cycle("", iface)
	if code != 0:
		break

curses.nocbreak()
screen.keypad(False)
curses.echo()
curses.endwin()
curses.curs_set(1)
screen.nodelay(0)

events.pyscord_thread_stop = 1
events.thread.join(3)

quit(0 if code >= 0 else code * -1);

