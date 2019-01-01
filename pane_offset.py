import draw

def render(jinx, s, e):
	w = len(f"{len(jinx):X}")
	cells = draw.Draw()
	cells.text(" ")
	if s <= jinx.position < e:
		cells.bold().fg(3).text(f"{jinx.position:0{w}X}")
	else:
		cells.text(f"{s:0{w}X}")
	cells.text(" ")
	return cells

def width(jinx, w):
	return 1+len(f"{len(jinx):X}")+1
