def render(out, jinx, s, e):
	w = len(f"{len(jinx):X}")
	out.text(" ")
	if s <= jinx.position < e:
		out.push().bold().fg(3).text(f"{jinx.position:0{w}X}").pop()
	else:
		out.text(f"{s:0{w}X}")
	out.text(" ")
	return out

def width(jinx, w):
	return 1+len(f"{len(jinx):X}")+1
