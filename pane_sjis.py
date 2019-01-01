import draw
from wcwidth import wcwidth

def render(jinx, s, e):
	l, p = len(jinx), jinx.position
	char2 = None # TODO
	cells = draw.Draw()
	cells.text(" ")
	for o in range(s, e):
		if char2:
			cells.push()
			if o == p:
				cells.fg(0).bg(7)
			if o == s:
				cells.str.write("\x1B[D")
				cells.dim().text(char2)

			cells.bg(None)
			cells.pop()
			char2 = None
		else:
			byte = jinx[o] if 0 <= o < l else None
			bytex = jinx[o+1] if 0 <= o+1 < l else None
			char2 = sjis2Table.get((byte, bytex))
			char = char2 or sjisTable.get(byte)

			cells.push()
			if o == p or char2 and o+1 == p:
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
	if not char2:
		cells.text(" ")
	return cells

def width(jinx, w):
	return 1+w+1

sjisTable = {}
sjis2Table = {}
for v in range(0x100):
	try: [sjisTable[v]] = bytes([v]).decode("sjis")
	except: pass
for v in range(0x100):
	for u in range(0x100):
		try:
			[ch] = bytes([v,u]).decode("sjis")
			sjis2Table[v,u] = ch if wcwidth(ch) == 2 else ch + " "
		except: pass
