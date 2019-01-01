import draw

def render(jinx, s, e):
	l, p = len(jinx), jinx.position
	cells = draw.Draw()
	cells.text(" ")

	for o in range(s, e):
		byte = jinx[o] if 0 <= o < l else None

		cells.push()
		if o == p:
			cells.fg(0).bg(7)

		if o > l:
			cells.text("  ")
		elif o == l:
			cells.dim().text("--")
		elif o == p and jinx.half:
			cells.text(f"-{byte&0xF:01X}")
		else:
			if byte == 0:
				cells.dim()
			cells.text(f"{byte:02X}")
		cells.bg(None)

		cells.text(" ")
		if (o+1-e) and not (o+1-s) % 8:
			cells.text(" ")
		cells.pop()
	return cells

def width(jinx, w):
	return 1+w*3 + (w-1)//8
