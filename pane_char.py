def render(out, jinx, s, e):
	l, p, enc = len(jinx), jinx.position, jinx.encoding
	out.text(" ")
	for o in range(s, e):
		byte = jinx[o] if 0 <= o < l else None
		char = charTable[enc, byte]

		out.push()
		if o == p:
			out.fg(0).bg(7)

		if o > l:
			out.text(" ")
		elif o == l:
			out.dim(1).text("-")
		elif o == p and jinx.half:
			out.dim().text("-")
		elif char is None:
			out.bold().fg(1).text("-")
		elif not char.isprintable():
			out.dim().text("·")
		else:
			out.text(char)

		out.bg(None)
		out.pop()
	out.text(" ")
	return out

def width(jinx, w):
	return w + 2

class CharDict(dict):
	def __missing__(self, key):
		if len(key) == 2:
			(enc, byte) = key
			try:
				[self[key]] = bytes([byte]).decode(enc)
			except: self[key] = None
			return self[key]
charTable = CharDict()
