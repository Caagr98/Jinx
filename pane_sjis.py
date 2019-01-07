from wcwidth import wcwidth
import pane_char

def render(out, jinx, s, e):
	l, p, enc = len(jinx), jinx.position, jinx.encoding
	char2 = None # TODO
	out.text(" ")
	for o in range(s, e):
		if char2:
			out.push()
			if o == p:
				out.invert()
				if jinx.char:
					out.cursor()
			if o == s:
				out.str.write("\x1B[D")
				out.dim().text(char2)

			out.bg(None)
			out.pop()
			char2 = None
		else:
			byte1 = jinx[o] if 0 <= o < l else None
			byte2 = jinx[o+1] if 0 <= o+1 < l else None
			char2 = sjisTable[enc, byte1, byte2]
			char = char2 or sjisTable[enc, byte1]

			out.push()
			if o == p or char2 and o+1 == p:
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
	if not char2:
		out.text(" ")
	return out

width = pane_char.width

class SjisDict(pane_char.CharDict):
	def __missing__(self, key):
		if len(key) == 3:
			(enc, byte1, byte2) = key
			try:
				[ch] = bytes([byte1, byte2]).decode("sjis")
				self[key] = ch if wcwidth(ch) == 2 else ch + " "
			except: self[key] = None
			return self[key]
		return super().__missing__(key)
sjisTable = SjisDict()
