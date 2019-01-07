from wcwidth import wcswidth

class Readline:
	__slots__ = ["_text", "_point", "scroll", "prefix", "width", "scrollOff"]
	def __init__(self, *, width=None, scrollOff=None, prefix=None):
		self._text = ""
		self._point = 0
		self.scroll = 0
		self.width = width
		self.scrollOff = scrollOff or 0
		self.prefix = prefix or ""

	@property
	def text(self):
		return self._text
	@text.setter
	def text(self, v):
		self._text = v
		self.point = self.point

	@property
	def point(self):
		return self._point
	@point.setter
	def point(self, v):
		self._point = max(0, min(v, len(self.text)))
		self.updateScroll()

	@property
	def displaytext(self):
		return self.prefix + self.text + " "
	@property
	def displaypoint(self):
		return len(self.prefix) + self.point

	def updateScroll(self):
		pointw = wcswidth(self.displaytext, self.displaypoint+1)
		self.scroll = max(self.scroll, pointw-self.width+self.scrollOff)
		self.scroll = min(self.scroll, pointw-self.scrollOff-wcswidth(self.displaytext[self.displaypoint]))
		self.scroll = min(self.scroll, wcswidth(self.displaytext)-self.width)
		self.scroll = max(self.scroll, 0)

	def input(self, key):
		if 0: pass
		elif key == "\x1B":    return False
		elif key == "\x1B[A":  self.hist(+1)
		elif key == "\x1B[B":  self.hist(-1)
		elif key == "\x1B[C":  self.move("right")
		elif key == "\x1B[D":  self.move("left")
		elif key == "\x1B[F":  self.move("end")
		elif key == "\x1B[H":  self.move("home")
		elif key == "\x7F" and not self.text: return False
		elif key == "\x7F":    self.kill("left")
		elif key == "\x1B[3~": self.kill("right")

		elif key == "\x01": self.move("home")
		elif key == "\x02": self.move("left")
		elif key == "\x03": return False
		elif key == "\x05": self.move("end")
		elif key == "\x06": self.move("right")
		elif key == "\x08": self.kill("left")
		elif key == "\x0A": a = self.text; self.text = ""; return a
		elif key == "\x0B": self.kill("end")
		elif key == "\x0E": self.hist(+1)
		elif key == "\x10": self.hist(-1)
		elif key == "\x15": self.kill("home")
		elif key == "\x17": self.kill_word()
		elif key.isprintable(): self.insert(key)
		return True

	def move(self, where):
		self.point = self.pos(where)
	def kill(self, where):
		pos = self.pos(where)
		if pos < self.point:
			self.text = self.text[:pos] + self.text[self.point:]
			self.point = pos
		else:
			self.text = self.text[:self.point] + self.text[pos:]
	def pos(self, where):
		return {
			"left":  self.point - 1,
			"right": self.point + 1,
			"home":  0,
			"end":   len(self.text),
		}[where]

	def insert(self, str):
		self.text = self.text[:self.point] + str + self.text[self.point:]
		self.point += len(str)

	def kill_word(self):
		p = self.point
		while p > 0:
			if not self.text[p-1].isspace(): break
			p -= 1
		while p > 0:
			if self.text[p-1].isspace(): break
			p -= 1
		self.text = self.text[:p] + self.text[self.point:]
		self.point = p

	def render(self, out):
		text = self.displaytext
		point = self.displaypoint

		l, r = self.scroll, self.scroll+self.width

		width = 0
		for i, ch in enumerate(text):
			width1 = width
			width2 = width+wcswidth(ch)
			width = width2

			if width2 <= l: continue
			if width1 >= r: break

			if i != 0 and width1 <= l < width2:
				out.push().dim().text("…" * (width2-l)).pop()
			elif i != len(text)-1 and width1 < r <= width2:
				out.push().dim().text("…" * (r-width1)).pop()
			elif i == point:
				out.push().cursor(True).text(ch).pop()
			else:
				out.text(ch)
		out.text(" " * (r - width))

if __name__ == "__main__":
	def main():
		import term
		import draw
		with term.raw(no_signals=True):
			rl = Readline(width=25, scrollOff=3)
			while True:
				input = term.getch().decode()
				result = rl.input(input)
				if result is False:
					break
				elif result is True:
					pass
				else:
					print("ok", result)
				# print(repr(rl.text), rl.point, rl.scroll)
				out = draw.Draw()
				rl.render(out)
				print("|" + str(out) + "|")
	main()
	del main
