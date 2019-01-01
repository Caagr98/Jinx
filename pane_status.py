import draw
import struct
import codecs
from wcwidth import wcwidth

endian = "little"

def render(jinx, width):
	ints = draw_ints(jinx, width)
	floats = draw_floats(jinx, width)
	strings = draw_strings(jinx, width - len(floats))
	strings.merge(floats)
	return [ints, strings]

def draw_ints(jinx, width):
	l, p = len(jinx), jinx.position

	ints = []
	totlen = 2
	n = 1

	while True:
		wu = len(str(0x100**n))
		ws = len(str(0x100**n//-2))
		curlen = 1+ws+2+wu+2
		if totlen + curlen > width: break
		totlen += curlen

		if p + n < l:
			u = int.from_bytes(byterange(jinx, p, n), endian)
			s = u - 0x100**n if u > 0x100**n//2 else u
		else:
			u = s = "-"
		n *= 2

		out = draw.Draw()
		out.text(f"[{u:{wu}} ")
		if u == s: out.dim()
		out.text(f"({s:{ws}})")
		out.dim(False)
		out.text(f"]")
		ints.append(out)

	surplus = width - totlen
	out = draw.Draw()
	out.text(" ")
	for n, s in enumerate(ints):
		out.merge(s)
		if n != len(ints)-1:
			part = surplus // (len(ints) - n-1)
			surplus -= part
			out.text(" " * part)
	out.text(" ")
	return out

def draw_floats(jinx, width):
	prefix = "<" if endian == "little" else ">"
	l, p = len(jinx), jinx.position
	f32 = str(struct.unpack(prefix + "f", byterange(jinx, p, 4))[0]) if p + 4 < l else "-"
	f64 = str(struct.unpack(prefix + "d", byterange(jinx, p, 8))[0]) if p + 8 < l else "-"

	out = draw.Draw()
	out.text(" [")
	out.text(f32)
	out.text("]  [")
	out.text(f64)
	out.text("] ")
	return out

def draw_strings(jinx, width):
	width -= 4
	def chunk():
		p = jinx.position
		while p < len(jinx):
			yield byterange(jinx, p, width)
			p += width
	string = decode_unknown(codecs.getincrementaldecoder(jinx.encoding)(), chunk())
	out = draw.Draw()
	strw = 0
	ellipsize = False
	chars = []
	for i, ch in enumerate(string):
		if strw + wcwidth(ch) <= width:
			chars.append(ch)
			strw += wcwidth(ch)
		else:
			if strw == width:
				strw -= wcwidth(chars.pop())
			ellipsize = True
			strw += 1
			break

	out.text(" [")
	out.text("".join(chars))
	if ellipsize:
		out.push().dim().text("…").pop()
	out.text(" " * (width - strw))
	out.text("] ")
	return out

def decode_unknown(dec, iter):
	for ch in iter:
		try:
			st = dec.getstate()
			chars = dec.decode(ch)
			for ch in chars:
				if ch.isprintable(): yield ch
				else: return
			continue
		except UnicodeError as e:
			dec.setstate(st)
			chars = dec.decode(ch[:e.start])
			for ch in chars:
				if ch.isprintable(): yield ch
				else: return
			break

def byterange(jinx, p, l):
	return bytes(jinx[n] for n in range(p, min(p+l, len(jinx))))
