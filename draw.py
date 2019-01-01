import wcwidth
import io

defaultFormat = (None, None, False, False)
class Draw:
	__slots__ = ["str", "_fg", "_bg", "_bold", "_dim", "_lastFmt", "stack", "len"]
	def __init__(self):
		self.str = io.StringIO()
		(self._fg, self._bg, self._bold, self._dim) = self._lastFmt = defaultFormat
		self.stack = []
		self.len = 0

	def push(self): self.stack.append((self._fg, self._bg, self._bold, self._dim)); return self
	def pop(self): (self._fg, self._bg, self._bold, self._dim) = self.stack.pop(); return self

	def fg(self, v): self._fg = v; return self
	def bg(self, v): self._bg = v; return self
	def bold(self, v=True): self._bold = v; return self
	def dim(self, v=True): self._dim = v; return self
	def text(self, text):
		self.len += wcwidth.wcswidth(text)
		fmt = (self._fg, self._bg, self._bold, self._dim)
		self.str.write(delta(self._lastFmt, fmt))
		self._lastFmt = fmt
		self.str.write(text)
		return self
	def merge(self, other):
		self.len += other.len
		self.str.write(other.str.getvalue())
		self._lastFmt = other._lastFmt
		return self

	def __len__(self):
		return self.len
	def __str__(self):
		return self.str.getvalue() + delta(self._lastFmt, defaultFormat)

def delta(old, new):
	if old != new:
		ofg, obg, obold, odim = old
		nfg, nbg, nbold, ndim = new
		tags = []
		if obold != nbold or odim != ndim:
			tags.append("22")
			if nbold: tags.append("1")
			if ndim: tags.append("2")
		if ofg != nfg: tags.append(f"38;5;{nfg}" if nfg is not None else "39")
		if obg != nbg: tags.append(f"48;5;{nbg}" if nbg is not None else "49")
		# return f"[{';'.join(tags)}]"
		return f"\x1B[{';'.join(tags)}m"
	return ""

log = []
