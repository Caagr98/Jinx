import pane_offset
import pane_hex
import pane_char
import pane_sjis
import pane_status
import draw
import os

class MainWindow:
	__slots__ = ["jinx", "scroll", "scrollOff", "uiHeight", "once", "width"]
	def __init__(self, jinx):
		self.jinx = jinx
		self.once = False
		self.scroll = 0
		self.scrollOff = 3
		self.uiHeight = 4
		self.width = 32
		self.scrollIntoView()

	def input(self, key):
		self.input_(key)
		self.scrollIntoView()
	def input_(self, key):
		if key == "\x03":    raise SystemExit
		if key == "\x1B":    self.jinx.commit(); self.jinx.insert = self.jinx.char = self.once = False; return
		if key == "\x1B[A":  self.move("up"); return
		if key == "\x1B[B":  self.move("down"); return
		if key == "\x1B[C":  self.move("right"); return
		if key == "\x1B[D":  self.move("left"); return
		if key == "\x1B[5~": self.move("pgup"); return
		if key == "\x1B[6~": self.move("pgdn"); return
		if key == "\x1B[F":  self.move("end"); return
		if key == "\x1B[H":  self.move("home"); return
		if key == "\x1B[2~": self.jinx.commit(); self.jinx.insert = not self.jinx.insert; return
		if key == "\t":      self.jinx.commit(); self.jinx.char = not self.jinx.char; return

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
		height = os.get_terminal_size()[1] - self.uiHeight
		self.jinx.commit()
		self.jinx.position = {
			"left":  self.jinx.position - 1,
			"right": self.jinx.position + 1,
			"up":    self.jinx.position - self.width,
			"down":  self.jinx.position + self.width,
			"pgup":  self.jinx.position - self.width * (height * 2//3),
			"pgdn":  self.jinx.position + self.width * (height * 2//3),
			"home":  self.jinx.position // self.width * self.width,
			"end":   self.jinx.position // self.width * self.width + self.width - 1,
			"top":   0,
			"bottom":len(self.jinx.buffer),
		}[how]

	def scrollIntoView(self):
		height = os.get_terminal_size()[1] - self.uiHeight
		line = self.jinx.position // self.width
		if line < self.scroll+self.scrollOff:
			self.scroll = line-self.scrollOff
		if line > self.scroll-(self.scrollOff-height):
			self.scroll = line+(self.scrollOff-height)
		self.scroll = max(0, min(self.scroll, len(self.jinx)//self.width-height))

	def render(self):
		height = os.get_terminal_size()[1] - self.uiHeight

		offsetW = pane_offset.width(self.jinx, self.width)
		hexW = pane_hex.width(self.jinx, self.width)
		charW = pane_char.width(self.jinx, self.width) if self.jinx.encoding != "sjis" else pane_sjis.width(self.jinx, self.width)

		out = draw.Draw()
		out.str.write("\x1B[2J")
		out.str.write("\x1B[H")
		out.text("═" * offsetW)
		out.text("╤")
		out.text("═" * hexW)
		out.text("╤")
		out.text("═" * charW)
		out.text("╕")

		out.str.write("\n")
		for s, e in ((i*self.width, (i+1)*self.width) for i in range(self.scroll, self.scroll+height)):
			out.merge(pane_offset.render(self.jinx, s, e))
			out.text("│" if self.jinx.char else "├")
			out.merge(pane_hex.render(self.jinx, s, e))
			out.text("├" if self.jinx.char else "┤")
			out.merge(pane_char.render(self.jinx, s, e) if self.jinx.encoding != "sjis" else pane_sjis.render(self.jinx, s, e))
			out.text("┤" if self.jinx.char else "│")
			out.str.write("\n")

		out.text("─" * offsetW)
		out.text("┴")
		out.text("─" * hexW)
		out.text("┴")
		out.text("─" * charW)
		out.text("┤")

		for line in pane_status.render(self.jinx, offsetW+1+hexW+1+charW):
			out.str.write("\n")
			out.merge(line)
			out.text("│")
		print(out, end="", flush=True)
