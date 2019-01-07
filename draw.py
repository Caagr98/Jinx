import wcwidth
import io

defaultFormat = (None, None, False, False, False)
class Draw:
	__slots__ = ["str", "_fg", "_bg", "_bold", "_dim", "_invert", "_cursor", "_lastFmt", "stack", "len"]
	def __init__(self):
		self.str = io.StringIO()
		(self._fg, self._bg, self._bold, self._dim, self._invert) = self._lastFmt = defaultFormat
		self._cursor = False
		self.stack = []
		self.len = 0

	def push(self): self.stack.append((self._fg, self._bg, self._bold, self._dim, self._invert, self._cursor)); return self
	def pop(self): (self._fg, self._bg, self._bold, self._dim, self._invert, self._cursor) = self.stack.pop(); return self

	def fg(self, v): self._fg = v; return self
	def bg(self, v): self._bg = v; return self
	def bold(self, v=True): self._bold = v; return self
	def dim(self, v=True): self._dim = v; return self
	def invert(self, v=None): self._invert = v if v is not None else not self._invert; return self
	def cursor(self): self._cursor = True; return self
	def pos(self, x, y): self.str.write(f"\x1B[{y+1};{x+1}H"); return self

	def raw(self, text):
		self.str.write(text)
		return self
	def text(self, text):
		if not text: return self
		if self._cursor:
			self._cursor = False
			self.raw(delta(self._lastFmt, defaultFormat)) # Because [s saves text style too
			self.raw("\x1B[s")
			self.raw(delta(defaultFormat, self._lastFmt))
			self.push().invert()
			self.text(text[0])
			self.pop()
			return self.text(text[1:])
		self.len += wcwidth.wcswidth(text)
		fmt = (self._fg, self._bg, self._bold, self._dim, self._invert)
		self.raw(delta(self._lastFmt, fmt)).raw(text)
		self._lastFmt = fmt
		return self
	def merge(self, other):
		self.len += other.len
		self.raw(other.str.getvalue())
		self._lastFmt = other._lastFmt
		return self

	def __len__(self):
		return self.len
	def __str__(self):
		return self.str.getvalue() + delta(self._lastFmt, defaultFormat)

def delta(old, new):
	if old != new:
		ofg, obg, obold, odim, oinvert = old
		nfg, nbg, nbold, ndim, ninvert = new
		tags = []
		if obold != nbold or odim != ndim:
			tags.append("22")
			if nbold: tags.append("1")
			if ndim: tags.append("2")
		if ofg != nfg: tags.append(f"38;5;{nfg}" if nfg is not None else "39")
		if obg != nbg: tags.append(f"48;5;{nbg}" if nbg is not None else "49")
		if oinvert != ninvert: tags.append("7" if ninvert else "27")
		# return f"\x1B[{';'.join(tags)}m[{';'.join(tags)}]"
		return f"\x1B[{';'.join(tags)}m"
	return ""

log = []
