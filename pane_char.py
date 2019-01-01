import draw

def render(jinx, s, e):
	l, p = len(jinx), jinx.position
	cells = draw.Draw()
	cells.text(" ")
	for o in range(s, e):
		byte = jinx[o] if 0 <= o < l else None
		char = charTable.get(byte)

		cells.push()
		if o == p:
			cells.fg(0).bg(7)

		if o > l:
			cells.text(" ")
		elif o == l:
			cells.dim(1).text("-")
		elif o == p and jinx.half:
			cells.dim().text("-")
		elif char is None:
			cells.bold().fg(1).text("-")
		elif not char.isprintable():
			cells.dim().text("·")
		else:
			cells.text(char)

		cells.bg(None)
		cells.pop()
	cells.text(" ")
	return cells

def width(jinx, w):
	return w + 2

charTable = {}
for v in range(0x100):
	try: [charTable[v]] = bytes([v]).decode("latin1")
	except: pass
