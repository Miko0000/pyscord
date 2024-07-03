import sys
import curses
import time
import types
import traceback

def ntos(string, width, space = ' '):
	if bool(string) is False:
		return ''

	result = ''

	list = string.split('\n')
	result += list[0]

	if len(list) <= 1:
		return result

	result += space * (width - len(list[0]))

	for line in list[1:len(list) - 1]:
		length = len(line)
		line += space * (width - length)
		result += line

	result += list[len(list) - 1]

	return result

class InterfaceRequest:
	origin = None
	target = None

	def __init__(self, origin, target):
		self.origin = origin
		self.target = target

	def resolve(self):
		self.target.resolve(self)

class Interface:
	buffer = [ '' ]
	state = 0
	options = {}
	interfaces = {}
	functions = {}
	def get(self, name):
		return self.interfaces[name]

	def invoke(self, function, *args):
		try:
			self.functions[function](self, *args)
		except:
			pass

	request_count = 0
	def request(origin):
		return NotImplemented

	def release(origin):
		return NotImplemented

	def state_change(self):
		return NotImplemented

	def state_change_unoccupied():
		pass

	def __init__(self, medium):
		self.medium = medium

class CursesInterface(Interface):
	_window = None

	@property
	def screen(self):
		return self.medium

	@property
	def window(self):
		if self._window is not None:
			return self._window

		return self.screen

	@window.setter
	def window(self, value):
		self._window = value

		return value

	def __init__(self, medium):
		super().__init__(medium)

class CursesOutputInterface(CursesInterface):
	prefix = ""

	def clear(self):
		self.buffer[0] = ''
		self.window.erase()
		self.window.refresh()

	formats = [

	]

	def format(self, prefix, on, off):
		wsize = self.window.getmaxyx()
		content = ntos(self.buffer[0], wsize[1])

		self.prefix = prefix
		self.formats.append([
			len(content),
			on,
			off
		])

	def format_normal(self):
		return self.format(
			"",
			-1,
			(curses.color_pair(1)
				| curses.color_pair(2)
				| curses.color_pair(3)
				| curses.A_BOLD
				| curses.COLOR_GREEN
				| curses.A_REVERSE
			)
		)

	def format_highlight(self):
		self.format(
			"",
			curses.A_REVERSE,
			-1
		)

	def format_options(self, slot):
		pair = 2 + (slot % 2)

		self.format(
			"",
			curses.color_pair(pair) | curses.COLOR_GREEN,
			-1
		)

		self("[%i] " % slot)

		self.format(
			"",
			curses.color_pair(pair) | curses.A_BOLD,
			curses.color_pair(pair) | curses.COLOR_GREEN,
		)


	def format_error(self):
		return self.format(
			"[error] ",
			curses.color_pair(1) | curses.A_BOLD,
			-1
		)

	def formats_shift(self, length):
		for format in self.formats:
			format[0] -= length

			if format[0] < 0:
				self.formats.remove(format)

	functions = {
		"clear":
			lambda self, *args: self.clear(),

		"f.normal":
			lambda self, *args: self.format_normal(),

		"f.error":
			lambda self, *args: self.format_error(),

		"f.highlight":
			lambda self, *args: self.format_highlight(),

		"f.options":
			lambda self, *args: self.format_options(*args)
	}

	def release(self):
		if self.request_count == -7:
			traceback.print_stack()

		self.request_count -= 1

	def request(self):
		ticket = self.request_count
		while self.request_count > ticket:
			pass

		self.request_count += 1

		while self.state > 0:
			pass

	def __call__(self, *args):
		global holder
		while self.state > 0:
			sys.stdout.write("e")
			time.sleep(0.5)
			pass

		holder2 = holder
		holder.request()
		holder = self
		curses.noecho()
		self.state = 1;

		if self.prefix:
			self.buffer[0] += self.prefix

		for arg in args:
			#arg = arg.replace('_', '__')
			self.buffer[0] += arg

		options = self.options
		window = self.window
		screen = self.screen
		wpos = window.getbegyx()
		wy = wpos[0]
		wx = wpos[1]

		wsize = window.getmaxyx()
		wcols = wsize[1]

		if options["border"]:
			window.box()
			wy += 1
			wx += 1

		try:
			self.buffer[0] = self.buffer[0][
				min(50000, len(self.buffer[0]))*-1:
			]
			length = (wsize[0] - 2)*(wsize[1] - 2)
			content = ntos(self.buffer[0], wcols)

			clen = len(content)
			dist = min(length, clen)
			dist = int(dist / wcols) * (wcols)

			if dist <= 0:
				dist = clen

			content = content[
				dist*-1:
			]

			screen.move(wy, wx)

			if len(self.formats) <= 0:
				screen.addstr(content)

				return done()

			#cpos = self.screen.getyx()
			#print('[', cpos[0], cpos[1], ']')
			screen.addstr(content[
				0:self.formats[0][0]]
			)

			if options["border"]:
				window.box()

			fpos = self.formats[0][0]
			i = 0
			fmtl = len(self.formats)
			while i < fmtl:
				format = self.formats[i]
				next = None

				if i < (fmtl - 1):
					next = self.formats[i + 1]

				if format[2] >= 0:
					screen.attroff(format[2])

				if format[1] >= 0:
					screen.attron(format[1])

				if not next:
					break

				#screen.addstr(str(format) + '\n')

				screen.addstr(
					content[fpos:next[0]]
				)

				if options["border"]:
					window.box()


				if next[2] >= 0:
					screen.attroff(next[2])

				if next[1] >= 0:
					screen.attron(next[1])

				fpos = next[0]

				i += 1

			screen.addstr(content[fpos:len(content) - 1])
			if options["border"]:
				window.box()

		except curses.error:
			pass

		except:
			pass

		# print(self.state)
		def done():
			curses.noecho()
			self.state = 0
			holder2.release()
			if options["border"]:
				window.box()

		return done()

	def __init__(self, screen):
		super().__init__(screen)
		self.invoke("f.normal")
		self.options["incoming"] = "Null"

class CursesInputInterface(CursesInterface):
	def state_change(self):
		pass

	def release(self):
		self.request_count -= 1

		pass

	def request(self):
		request_count = self.request_count
		ticket = request_count

		while request_count > ticket:
			pass

		self.request_count += 1

		while self.state > 0:
			if self.state == 2:
				break

		#curses.flushinp()

	def __call__(self):
		options = self.options
		screen = self.screen
		window = self.window

		border = options["border"]

		if border is True:
			window.box()
			screen.refresh()

		global holder
		while self.state > 0:
			pass

		holder2 = holder
		holder2.request()
		holder = self
		self.state = 1

		wpos = window.getbegyx()
		wsize = window.getmaxyx()

		prefix = options["prefix"]
		plen = len(prefix)

		if border is True:
			wpos = (wpos[0] + 1, wpos[1] + 1)
			window.box()
			window.refresh()
			screen.refresh()

		screen.move(wpos[0], wpos[1])
		screen.addstr(prefix)

		holder2.release()

		time.sleep(0)
		self.state = 2
		data = ''
		try:
			data = screen.getkey()
		except:
			pass

		while data.find('\n') < 0:
			holder2.request()
			#screen.move(wpos[0], wpos[1] + plen)
			screen.addstr(data)

			#curses.echo()
			key = ''
			try:
				key = screen.getkey()
			except:
				pass

			if key in ('KEY_BACKSPACE', '\b', '\x7f'):
				data = data[0:-1]
			elif key == '\n':
				holder2.release()

				break
			else:
				data += key

			screen.clrtoeol()
			screen.move(wpos[0], wpos[1] + plen)
			if border is True:
				window.box()
				screen.refresh()

			# Let other thread run for a moment
			holder2.release()
			time.sleep(0)

		curses.noecho()
		screen.move(wpos[0], wpos[1] + plen)
		screen.clrtoeol()
		if border is True:
			window.box()
			screen.refresh()

		screen.refresh()
		self.state = 0

		return data

	def __init__(self, screen):
		super().__init__(screen)
		self.options["prefix"] = "> "
		self.options["border"] = True

curses.init_pair(1, curses.COLOR_RED, curses.COLOR_WHITE)
curses.init_pair(2, 184, 28)
curses.init_pair(3, 226, 34)

def iface(screen):
	iface = CursesInterface(screen)
	box = iface.screen.subwin(
		curses.LINES - 3,
		curses.COLS,
		0,
		0
	)
	box.box()
	iface.interfaces["output"] = CursesOutputInterface(screen)
	iface.interfaces["output"].options["border"] = True
	iface.interfaces["output"].window = box
	box = iface.screen.subwin(
		3,
		curses.COLS,
		curses.LINES - 3,
		0
	)
	box.box()
	screen.refresh()
	iface.interfaces["input"] = CursesInputInterface(screen)
	iface.interfaces["input"].window = box

	return iface

holder = Interface(None)
