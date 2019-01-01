import draw
from wcwidth import wcwidth

def render(jinx, s, e):
	l, p = len(jinx), jinx.position
	char2 = None # TODO
	out = draw.Draw()
	out.text(" ")
	for o in range(s, e):
		if char2:
			out.push()
			if o == p:
				out.fg(0).bg(7)
			if o == s:
				out.str.write("\x1B[D")
				out.dim().text(char2)

			out.bg(None)
			out.pop()
			char2 = None
		else:
			byte = jinx[o] if 0 <= o < l else None
			bytex = jinx[o+1] if 0 <= o+1 < l else None
			char2 = sjis2Table.get((byte, bytex))
			char = char2 or sjisTable.get(byte)

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
