import os
import contextlib
from math import floor, ceil

import pane_offset
import pane_hex
import pane_char
import pane_sjis
import pane_status
import draw
import readline

class Repaint(BaseException): pass

class MainWindow:
	__slots__ = ["jinx", "scroll", "scrollOff", "uiTop", "uiBottom", "once", "width", "_prompt", "rl"]
	def __init__(self, jinx):
		self.jinx = jinx
		self.once = False
		self.scroll = 0
		self.scrollOff = 3
		self.uiTop, self.uiBottom = 1, 3
		self.width = 32
		self.scrollIntoView()
		self.prompt = None

	@property
	def displaywidth(self):
		offsetW = pane_offset.width(self.jinx, self.width)
		hexW = pane_hex.width(self.jinx, self.width)
		charW = (pane_char if self.jinx.encoding != "sjis" else pane_sjis).width(self.jinx, self.width)
		return offsetW, hexW, charW

	def input(self, key):
		with self.repainting():
			if key == "~resize~": raise Repaint()
			if key == "\x0C":     raise Repaint()

			if self.prompt:
				self.rl.scrollOff = self.scrollOff
				self.rl.width = sum(self.displaywidth)-14
				result = self.rl.input(key)
				if result is False:
					self.prompt.cancel()
					self.prompt = None
				elif result is True:
					self.prompt.update(self.rl.text)
				else:
					self.prompt.accept(result)
					self.prompt = None
					raise Repaint()
				return

			norm = not self.jinx.insert and not self.jinx.char

			if 0: pass
			elif key == "\x03":     raise SystemExit # ^C
			elif key == "\x1B":     self.jinx.commit(); self.jinx.insert = self.jinx.char = self.once = False
			elif key == "\x1B[A":   self.move("up")
			elif key == "\x1B[B":   self.move("down")
			elif key == "\x1B[C":   self.move("right")
			elif key == "\x1B[D":   self.move("left")
			elif key == "\x1B[5~":  self.move("pgup")
			elif key == "\x1B[6~":  self.move("pgdn")
			elif key == "\x1B[F":   self.move("end")
			elif key == "\x1B[H":   self.move("home")
			elif key == "\x09":     self.jinx.commit(); self.jinx.char = not self.jinx.char # ^I tab
			elif key == "\x1B[2~":  self.jinx.commit(); self.jinx.insert = not self.jinx.insert
			elif key == "\x1B[3~":  self.jinx.begin(); self.jinx.end += 1
			elif key == "\x7F":     self.jinx.begin(); self.jinx.erase()
			elif norm and key == "h": self.move("left")
			elif norm and key == "j": self.move("down")
			elif norm and key == "k": self.move("up")
			elif norm and key == "l": self.move("right")
			elif norm and key == "H": self.move("home")
			elif norm and key == "L": self.move("end")
			elif norm and key == "^": self.move("home")
			elif norm and key == "$": self.move("end")
			elif norm and key == "g": self.move("top")
			elif norm and key == "G": self.move("bottom")
			elif norm and key == "x": self.jinx.begin(); self.jinx.written.append(0); self.jinx.end += 1
			elif norm and key == "r": self.jinx.commit(); self.jinx.char = self.once = True
			elif norm and key == "R": self.jinx.commit(); self.jinx.char = True
			elif norm and key == "i": self.jinx.commit(); self.jinx.insert = True
			elif norm and key == "I": self.jinx.commit(); self.jinx.char = self.jinx.insert = True
			elif norm and key == "u": self.jinx.commit(); self.jinx.undo()
			elif norm and key == "U": self.jinx.commit(); self.jinx.redo()
			elif norm and key == "\x12": self.jinx.commit(); self.jinx.redo() # ^R
			elif norm and key == "/": self.jinx.commit(); self.prompt = SeekPrompt(self)
			elif norm and key == ":": self.jinx.commit(); self.prompt = CommandPrompt(self)
			elif self.jinx.write_key(key):
				if self.once: self.jinx.commit(); self.jinx.insert = self.jinx.char = self.once = False

	def move(self, where):
		self.jinx.commit()
		self.jinx.position = self.pos(where)

	def pos(self, where):
		height = os.get_terminal_size()[1] - self.uiTop - self.uiBottom
		return {
			"left":  self.jinx.position - 1,
			"right": self.jinx.position + 1,
			"up":    self.jinx.position - self.width,
			"down":  self.jinx.position + self.width,
			"pgup":  self.jinx.position - self.width * floor(height * 2 / 3),
			"pgdn":  self.jinx.position + self.width * floor(height * 2 / 3),
			"home":  floor(self.jinx.position / self.width) * self.width,
			"end":   ceil(self.jinx.position / self.width) * self.width - 1,
			"top":   0,
			"bottom":len(self.jinx.buffer),
		}[where]

	def scrollIntoView(self):
		height = os.get_terminal_size()[1] - self.uiTop - self.uiBottom
		line = self.jinx.position // self.width
		if line < self.scroll+self.scrollOff:
			self.scroll = line-self.scrollOff
		if line > self.scroll-(self.scrollOff-height):
			self.scroll = line+(self.scrollOff-height)
		self.scroll = max(0, min(self.scroll, ceil((len(self.jinx)+1)/self.width)-height))

	@contextlib.contextmanager
	def repainting(self):
		def lineset(a, b):
			return set(range(min(a, b), max(a,b)+1))
		s, l, p = self.scroll, len(self.jinx), self.jinx.position
		try:
			yield
		except Repaint:
			self.render()
		else:
			self.scrollIntoView()
			height = os.get_terminal_size()[1] - self.uiTop - self.uiBottom
			s2, l2, p2 = self.scroll, len(self.jinx), self.jinx.position
			lines = {p2 // self.width}
			prefix = ""
			if (s2, l2, p2) != (s, l, p):
				lines |= lineset(p // self.width, p2 // self.width)
				if l != l2:
					lines |= lineset(p // self.width, self.scroll+height)
				if abs(s-s2) >= height:
					lines |= lineset(self.scroll, self.scroll+height)
				if 0 < s-s2 < height:
					prefix += f"\x1B[{self.uiTop+1};{self.uiTop+height+1}r\x1B[{s-s2}T\x1B[r"
					lines |= lineset(self.scroll, self.scroll+(s2-s))
				if 0 < s2-s < height:
					prefix += f"\x1B[{self.uiTop+1};{self.uiTop+height+1}r\x1B[{s2-s}S\x1B[r"
					lines |= lineset(self.scroll+height-(s2-s), self.scroll+height)
			self.render(lines, prefix=prefix)

	def render(self, lines=None, *, prefix="\x1B[2J"):
		height = os.get_terminal_size()[1] - self.uiTop - self.uiBottom

		offsetW, hexW, charW = self.displaywidth

		out = draw.Draw()
		out.raw(prefix)

		out.pos(0, 0                ).text("═" * offsetW).text("╤").text("═" * hexW).text("╤").text("═" * charW).text("╕")
		out.pos(0, self.uiTop+height).text("─" * offsetW).text("┴").text("─" * hexW).text("┴").text("─" * charW).text("┤")

		for line in pane_status.render(self.jinx, offsetW+1+hexW+1+charW):
			out.raw("\n").merge(line).text("│")

		if lines is None: lines = range(self.scroll,self.scroll+height)
		for i in lines:
			if i not in range(self.scroll, self.scroll+height): continue
			s, e = i*self.width, (i+1)*self.width
			out.pos(0, self.uiTop+i-self.scroll)
			pane_offset.render(out, self.jinx, s, e)
			out.text("│")
			pane_hex.render(out, self.jinx, s, e)
			out.text("│")
			(pane_char if self.jinx.encoding != "sjis" else pane_sjis).render(out, self.jinx, s, e)
			out.text("│")

		if self.prompt:
			out.pos(7, self.uiTop+height)
			out.text("[")
			self.rl.render(out)
			out.text("]")

		out.pos(7, 0)
		out.text("[")
		if self.jinx.modified:
			out.push().dim().text("*").pop()
		if self.jinx.fname:
			out.pretty(self.jinx.fname, width=sum(self.displaywidth)-14-self.jinx.modified)
		else:
			out.push().dim().text("<No name>").pop()
		out.text("]")

		out.raw("\x1B[u")

		print(out, end="", flush=True)

	@property
	def prompt(self):
		return self._prompt
	@prompt.setter
	def prompt(self, v):
		if v is None:
			self.rl = self._prompt = None
		else:
			self.rl = readline.Readline(prefix=v.prefix())
			self.rl.scrollOff = self.scrollOff
			self.rl.width = sum(self.displaywidth)-14
			self._prompt = v

class SeekPrompt:
	__slots__ = ["ui", "origpos", "origscroll"]
	def __init__(self, ui):
		self.ui = ui
		self.origpos, self.origscroll = self.ui.jinx.position, self.ui.scroll
	def prefix(self): return "/"
	def cancel(self): self.ui.jinx.position, self.ui.scroll = self.origpos, self.origscroll
	def update(self, string):
		try:
			self.ui.jinx.position = int(string, 16)
		except ValueError:
			self.cancel()
	accept = update

class CommandPrompt:
	__slots__ = ["ui"]
	def __init__(self, ui):
		self.ui = ui
	def prefix(self): return ":"
	def cancel(self): pass
	def update(self, string): pass
	def accept(self, string):
		cmd, arg = string.split(" ", 1) if " " in string else (string, None)
