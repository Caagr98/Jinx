def render(out, jinx, s, e):
	l, p = len(jinx), jinx.position
	out.text(" ")
	for o in range(s, e):
		byte = jinx[o] if 0 <= o < l else None

		out.push()
		if o == p:
			out.cursor(not jinx.char)

		if o > l:
			out.text("  ")
		elif o == l:
			out.dim().text("--")
		elif o == p and jinx.half:
			out.text(f"-{byte&0xF:01X}")
		else:
			if byte == 0:
				out.dim()
			out.text(f"{byte:02X}")
		out.bg(None)
		out.invert(0)

		out.text(" ")
		if (o+1-e) and not (o+1-s) % 8:
			out.text(" ")
		out.pop()
	return out

def width(jinx, w):
	return 1+w*3 + (w-1)//8
