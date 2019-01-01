import draw

def render(jinx, s, e):
	l, p = len(jinx), jinx.position
	out = draw.Draw()
	out.text(" ")
	for o in range(s, e):
		byte = jinx[o] if 0 <= o < l else None
		char = charTable.get(byte)

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

charTable = {}
for v in range(0x100):
	try: [charTable[v]] = bytes([v]).decode("latin1")
	except: pass
