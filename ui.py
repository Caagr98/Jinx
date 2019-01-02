import os
import contextlib
from math import floor, ceil

import pane_offset
import pane_hex
import pane_char
import pane_sjis
import pane_status
import draw

class Repaint(BaseException): pass

class MainWindow:
	__slots__ = ["jinx", "scroll", "scrollOff", "uiTop", "uiBottom", "once", "width"]
	def __init__(self, jinx):
		self.jinx = jinx
		self.once = False
		self.scroll = 0
		self.scrollOff = 3
		self.uiTop, self.uiBottom = 1, 3
		self.width = 32
		self.scrollIntoView()

	def input(self, key):
		with self.repainting():
			if key == "~resize~": raise Repaint()
			if key == "\x0C":     raise Repaint()
			if key == "\x03":     raise SystemExit
			if key == "\x1B":     self.jinx.commit(); self.jinx.insert = self.jinx.char = self.once = False; return
			if key == "\x1B[A":   self.move("up"); return
			if key == "\x1B[B":   self.move("down"); return
			if key == "\x1B[A":   self.move("up"); return
			if key == "\x1B[B":   self.move("down"); return
			if key == "\x1B[C":   self.move("right"); return
			if key == "\x1B[D":   self.move("left"); return
			if key == "\x1B[5~":  self.move("pgup"); return
			if key == "\x1B[6~":  self.move("pgdn"); return
			if key == "\x1B[F":   self.move("end"); return
			if key == "\x1B[H":   self.move("home"); return
			if key == "\x1B[2~":  self.jinx.commit(); self.jinx.insert = not self.jinx.insert; return
			if key == "\t":       self.jinx.commit(); self.jinx.char = not self.jinx.char; return

			if not self.jinx.insert and not self.jinx.char:
				if key == "h": self.move("left"); return
				if key == "j": self.move("down"); return
				if key == "k": self.move("up"); return
				if key == "l": self.move("right"); return
				if key == "H": self.move("home"); return
				if key == "L": self.move("end"); return
				if key == "^": self.move("home"); return
				if key == "$": self.move("end"); return
				if key == "g": self.move("top"); return
				if key == "G": self.move("bottom"); return
				if key == "x": self.jinx.begin(); self.jinx.written.append(0); self.jinx.end += 1; return
				if key == "r": self.jinx.commit(); self.jinx.char = self.once = True; return
				if key == "R": self.jinx.commit(); self.jinx.char = True; return
				if key == "i": self.jinx.commit(); self.jinx.insert = True; return
				if key == "I": self.jinx.commit(); self.jinx.char = self.jinx.insert = True; return
				if key == "u": self.jinx.commit(); self.jinx.undo(self._undo, self._redo); return
				if key == "U": self.jinx.commit(); self.jinx.undo(self._redo, self._undo); return
				if key == "\x12": self.jinx.commit(); self.jinx.undo(self._redo, self._undo); return

			if key == "\x1B[3~": self.jinx.begin(); self.jinx.end += 1; return
			if key == "\x7F": self.jinx.begin(); self.jinx.erase(); return
			if self.jinx.write_key(key) and self.once: self.jinx.commit(); self.jinx.insert = self.jinx.char = self.once = False; return

	def move(self, how):
		height = os.get_terminal_size()[1] - self.uiTop - self.uiBottom
		self.jinx.commit()
		self.jinx.position = {
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
		}[how]

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
				if s2 < s:
					prefix += f"\x1B[{self.uiTop+1};{self.uiTop+height+1}r\x1B[{s-s2}T\x1B[r"
					lines |= lineset(self.scroll, self.scroll+(s2-s))
				if s2 > s:
					prefix += f"\x1B[{self.uiTop+1};{self.uiTop+height+1}r\x1B[{s2-s}S\x1B[r"
					lines |= lineset(self.scroll+height-(s2-s), self.scroll+height)
			self.render(lines, prefix=prefix)

	def render(self, lines=None, *, prefix="\x1B[2J"):
		height = os.get_terminal_size()[1] - self.uiTop - self.uiBottom

		offsetW = pane_offset.width(self.jinx, self.width)
		hexW = pane_hex.width(self.jinx, self.width)
		charW = (pane_char if self.jinx.encoding != "sjis" else pane_sjis).width(self.jinx, self.width)

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
			out.text("│" if self.jinx.char else "├")
			pane_hex.render(out, self.jinx, s, e)
			out.text("├" if self.jinx.char else "┤")
			(pane_char if self.jinx.encoding != "sjis" else pane_sjis).render(out, self.jinx, s, e)
			out.text("┤" if self.jinx.char else "│")

		print(out, end="", flush=True)
