import draw

def render(jinx, s, e):
	w = len(f"{len(jinx):X}")
	out = draw.Draw()
	out.text(" ")
	if s <= jinx.position < e:
		out.bold().fg(3).text(f"{jinx.position:0{w}X}")
	else:
		out.text(f"{s:0{w}X}")
	out.text(" ")
	return out

def width(jinx, w):
	return 1+len(f"{len(jinx):X}")+1
